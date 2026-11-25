"""Zenodo 29193의 공개 비행 자료를 체크섬과 진행 기록과 함께 받는다."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

RECORD = "https://zenodo.org/api/records/29193"
FILES = ("README.txt", "experiments.csv", "genotype2line.csv",
         "trials.csv.gz", "minifly.py", "minifly-out.txt", "series.h5")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def hashes(path):
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            md5.update(chunk)
            sha.update(chunk)
    return md5.hexdigest(), sha.hexdigest()


def download_ranges(url, destination, size, expected_md5, progress):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock
    chunk_size = 32 * 1024 * 1024
    count = (size + chunk_size - 1) // chunk_size
    parts = destination.with_suffix(".parts")
    parts.mkdir(exist_ok=True)
    marker = parts / "source.json"
    source = dict(url=url, bytes=size, md5=expected_md5, chunkSize=chunk_size)
    if marker.exists() and json.loads(marker.read_text(encoding="utf-8")) != source:
        raise ValueError("부분 자료의 출처가 현재 원본과 다릅니다.")
    write_json(marker, source)
    counters, lock = {}, Lock()
    updated = [0.]
    started = time.monotonic()
    def report(index, length):
        with lock:
            counters[index] = length
            now = time.monotonic()
            if now - updated[0] >= 5:
                progress("downloading_ranges", file="series.h5", bytes=sum(counters.values()),
                         total=size, elapsedSeconds=now-started, workers=16)
                updated[0] = now
    def one(index):
        first, end = index * chunk_size, min((index+1)*chunk_size, size)-1
        target = parts / f"{index:04d}.part"
        length = end-first+1
        for attempt in range(5):
            offset = target.stat().st_size if target.exists() else 0
            report(index, offset)
            if offset == length:
                return
            if offset > length:
                raise ValueError("부분 자료의 크기가 맞지 않습니다.")
            try:
                request = urllib.request.Request(url, headers={
                    "User-Agent": "FlyTracker/flight-calibration",
                    "Range": f"bytes={first+offset}-{end}"})
                with urllib.request.urlopen(request, timeout=60) as response:
                    if response.status != 206 or not response.headers.get("Content-Range", "").startswith(f"bytes {first+offset}-"):
                        raise ValueError("서버가 요청한 부분 다운로드 범위를 반환하지 않았습니다.")
                    with target.open("ab") as stream:
                        while chunk := response.read(1024*1024):
                            stream.write(chunk)
                            offset += len(chunk)
                            if offset > length:
                                raise ValueError("부분 자료가 예상 크기를 넘었습니다.")
                            report(index, offset)
                if offset != length:
                    raise OSError("부분 자료가 중간에 끝났습니다.")
                report(index, offset)
                return
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(2**attempt)
    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(one, range(count)))
    progress("assembling", file="series.h5", bytes=size, total=size)
    with destination.open("wb") as output:
        for index in range(count):
            with (parts / f"{index:04d}.part").open("rb") as source_stream:
                while chunk := source_stream.read(8*1024*1024):
                    output.write(chunk)


def fetch(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    progress_path = directory.parent / "download-progress.json"
    def progress(state, **values):
        data = dict(state=state, utc=datetime.now(timezone.utc).isoformat(), **values)
        write_json(progress_path, data)
        print(json.dumps(data), flush=True)
    request = urllib.request.Request(RECORD, headers={"User-Agent": "FlyTracker/flight-calibration"})
    with urllib.request.urlopen(request, timeout=45) as response:
        record = json.load(response)
    write_json(directory / "record.json", record)
    by_name = {row["key"]: row for row in record["files"]}
    manifest = dict(record=29193, source=RECORD, updated=record["updated"],
                    license=record["metadata"].get("license"), files={})
    for name in FILES:
        row = by_name[name]
        target = directory / name
        expected_md5 = row["checksum"].removeprefix("md5:")
        expected_size = row["size"]
        if name == "series.h5" and not target.exists():
            download_ranges(f"https://zenodo.org/records/29193/files/{name}?download=1",
                            directory / (name + ".part"), expected_size, expected_md5, progress)
        if target.exists():
            md5, sha = hashes(target)
            if target.stat().st_size != expected_size or md5 != expected_md5:
                raise ValueError("기존 파일의 체크섬이 다릅니다: " + str(target))
        else:
            part = directory / (name + ".part")
            started = time.monotonic()
            for attempt in range(3):
                try:
                    offset = part.stat().st_size if part.exists() else 0
                    if offset > expected_size:
                        raise ValueError("부분 파일 크기가 예상보다 큽니다.")
                    if offset < expected_size:
                        headers = {"User-Agent": "FlyTracker/flight-calibration"}
                        if offset:
                            headers["Range"] = f"bytes={offset}-"
                        url = f"https://zenodo.org/records/29193/files/{name}?download=1"
                        request = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(request, timeout=45) as response:
                            if offset and response.status == 206:
                                content_range = response.headers.get("Content-Range", "")
                                if not content_range.startswith(f"bytes {offset}-"):
                                    raise ValueError("서버의 부분 파일 범위가 다릅니다.")
                                mode = "ab"
                            else:
                                offset, mode = 0, "wb"
                            progress("downloading", file=name, bytes=offset, total=expected_size)
                            updated = 0.
                            with part.open(mode) as stream:
                                while chunk := response.read(1024 * 1024):
                                    stream.write(chunk)
                                    offset += len(chunk)
                                    if offset > expected_size:
                                        raise ValueError("다운로드가 예상 크기를 넘었습니다.")
                                    now = time.monotonic()
                                    if now - updated >= 5:
                                        progress("downloading", file=name, bytes=offset,
                                                 total=expected_size, elapsedSeconds=now-started)
                                        updated = now
                                    if now - started > 1200:
                                        raise TimeoutError("파일 다운로드의 20분 상한을 넘었습니다.")
                    progress("verifying", file=name, bytes=part.stat().st_size, total=expected_size)
                    md5, sha = hashes(part)
                    if part.stat().st_size != expected_size or md5 != expected_md5:
                        raise ValueError("공개 원본 MD5 또는 크기와 일치하지 않습니다: " + name)
                    part.replace(target)
                    break
                except (OSError, TimeoutError) as exc:
                    progress("retrying", file=name, attempt=attempt+1, error=str(exc))
                    if attempt == 2:
                        raise
                    time.sleep(2)
        manifest["files"][name] = dict(bytes=expected_size, md5=md5, sha256=sha)
        write_json(directory / "manifest.json", manifest)
        progress("file_verified", file=name, bytes=expected_size, sha256=sha)
    progress("completed", files=len(FILES))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()
    fetch(args.directory)


if __name__ == "__main__":
    main()
