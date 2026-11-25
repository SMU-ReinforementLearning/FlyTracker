"""공개 자료 다운로드의 재개와 잘못된 서버 응답 및 캐시 보호를 검사한다."""

import hashlib
import io
import json
import re

import pytest

from scripts import fetch_flight_dataset as downloader


class Response(io.BytesIO):
    def __init__(self,body,status=200,headers=None):
        super().__init__(body)
        self.status=status
        self.headers=headers or {}


def test_range_download_resumes_part_and_assembles_exact_bytes(tmp_path,monkeypatch):
    data=bytes(range(128))
    calls=[]
    def open_url(request,timeout):
        match=re.fullmatch(r"bytes=(\d+)-(\d+)",request.get_header("Range"))
        first,last=map(int,match.groups());calls.append((first,last))
        return Response(data[first:last+1],206,{"Content-Range":f"bytes {first}-{last}/{len(data)}"})
    monkeypatch.setattr(downloader.urllib.request,"urlopen",open_url)
    destination=tmp_path/"series.h5.part"
    parts=destination.with_suffix(".parts");parts.mkdir()
    (parts/"0000.part").write_bytes(data[:13])
    downloader.download_ranges("https://example.invalid/data",destination,len(data),
                               hashlib.md5(data).hexdigest(),lambda *args,**kw:None)
    assert calls==[(13,len(data)-1)]
    assert destination.read_bytes()==data


def test_range_download_rejects_ignored_range(tmp_path,monkeypatch):
    monkeypatch.setattr(downloader.urllib.request,"urlopen",
                        lambda *args,**kwargs:Response(b"wrong",200))
    destination=tmp_path/"series.h5.part"
    with pytest.raises(ValueError,match="부분 다운로드 범위"):
        downloader.download_ranges("https://example.invalid/data",destination,5,
                                    "irrelevant",lambda *args,**kw:None)
    assert not destination.exists()


def test_existing_bad_cache_is_reported_and_preserved(tmp_path,monkeypatch):
    record=dict(updated="fixed",metadata={"license":{"id":"cc-by-4.0"}},files=[
        dict(key="tiny.dat",size=4,checksum="md5:"+hashlib.md5(b"good").hexdigest())])
    monkeypatch.setattr(downloader,"FILES",("tiny.dat",))
    monkeypatch.setattr(downloader.urllib.request,"urlopen",
                        lambda *args,**kwargs:Response(json.dumps(record).encode()))
    (tmp_path/"tiny.dat").write_bytes(b"wrong")
    with pytest.raises(ValueError,match="기존 파일"):
        downloader.fetch(tmp_path)
    assert (tmp_path/"tiny.dat").read_bytes()==b"wrong"
