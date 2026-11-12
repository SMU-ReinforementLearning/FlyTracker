"""확장 비행 회로를 로컬 원자료에서 메모리로만 읽는다. CSV를 생성하지 않는다."""
from collections import Counter, defaultdict
import csv
import hashlib
from threading import RLock


CORE_TYPES = frozenset(('LC4','LPLC1','DNp03','DNa15','DNb01','VES041'))
_CACHE = {}
_LOCK = RLock()


def expand_flight_network(backend):
    """실제 연결만 유지한 유도 부분 그래프. 추가 입력의 구동은 별도 모델 가정이다."""
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise ValueError('확장 신경 비행에는 pyarrow가 필요합니다. uv sync --extra neural을 실행하세요.') from exc
    sources = {
        'raw_connectivity': backend.root/'data/raw/Drosophila_brain_model/Connectivity_783.parquet',
        'raw_annotations': backend.root/'data/raw/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv',
    }
    try:
        hashes = {k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in sources.items()}
    except OSError as exc:
        raise ValueError(f'확장 비행 회로의 로컬 원자료를 읽지 못했습니다: {exc}') from exc
    key = tuple(sorted({**backend.hashes,**hashes}.items()))
    with _LOCK:
        if key not in _CACHE:
            annotation = {}
            with sources['raw_annotations'].open(encoding='utf-8') as handle:
                for row in csv.DictReader(handle,delimiter='\t'):
                    annotation[int(row['root_id'])] = {k:row[k] for k in ('cell_type','side','top_nt','top_nt_conf')}
            core = {root for root,n in annotation.items() if n['cell_type'] in CORE_TYPES}
            found = {annotation[root]['cell_type'] for root in core}
            if found != CORE_TYPES:
                raise ValueError(f'원자료에 필요한 비행 뉴런 주석이 없습니다: {sorted(CORE_TYPES-found)}')
            targets = {root for root in core if annotation[root]['cell_type'] in ('DNp03','DNa15','DNb01','VES041')}
            columns = ['Presynaptic_ID','Postsynaptic_ID','Connectivity','Excitatory']
            incoming = pq.read_table(sources['raw_connectivity'],columns=columns,
                                     filters=[('Postsynaptic_ID','in',sorted(targets))])
            partners = defaultdict(list)
            for pre,post,count,sign in zip(*(incoming[c].to_pylist() for c in columns)):
                if pre in annotation and pre != post and count >= 5 and sign > 0 and pre not in core:
                    partners[post].append((int(count),int(pre)))
            background, extra = set(),set()
            for post,choices in partners.items():
                picked = {pre for count,pre in sorted(choices,key=lambda x:(-x[0],x[1]))[:3]}
                extra.update(picked)
                if annotation[post]['cell_type'] in ('DNa15','DNb01'):
                    background.update(picked)
            base_ids = {int(x) for x in backend.circuit.ids}
            chosen = base_ids | core | extra
            table = pq.read_table(sources['raw_connectivity'],columns=columns,
                                  filters=[('Presynaptic_ID','in',sorted(chosen)),('Postsynaptic_ID','in',sorted(chosen))])
            # 같은 연결의 여러 행은 원래 부호와 시냅스 수를 검증한 뒤 합친다.
            measured = {}
            for pre,post,count,sign in zip(*(table[c].to_pylist() for c in columns)):
                pair = str(pre),str(post)
                if count <= 0 or sign not in (-1,1):
                    raise ValueError('원자료의 연결 수 또는 부호가 올바르지 않습니다.')
                old_count,old_sign = measured.get(pair,(0,int(sign)))
                if old_sign != sign: raise ValueError('같은 연결에 서로 다른 부호가 있습니다.')
                measured[pair] = old_count+int(count),old_sign
            for a,b,count in zip(backend.circuit.pre,backend.circuit.post,backend.circuit.signed_counts):
                pair = backend.circuit.ids[a],backend.circuit.ids[b]
                found_count,found_sign = measured.get(pair,(0,1))
                if found_count*found_sign != count:
                    raise ValueError('원자료와 기존 가공 CSV의 연결 수 또는 부호가 일치하지 않습니다.')
            nodes = []
            base_selection = {int(n['id']):n['selection'] for n in backend.circuit.nodes}
            # 원래 뉴런 순서를 보존하고 추가 뉴런은 고정된 순서로 붙인다.
            order = [int(i) for i in backend.circuit.ids] + sorted(chosen-base_ids)
            for root in order:
                nodes.append(dict(id=str(root),**annotation[root],
                                  selection=base_selection.get(root,'flight_core' if root in core else 'flight_input'),
                                  excluded_in_synapses='not_recomputed',excluded_out_synapses='not_recomputed'))
            edges = [dict(pre=a,post=b,synapse_count=count,source_model_sign=sign)
                     for (a,b),(count,sign) in sorted(measured.items())]
            circuit = type(backend.circuit)(nodes,edges)
            idx = {int(root):i for i,root in enumerate(circuit.ids)}
            inputs = dict(background=tuple(sorted(idx[root] for root in background)),
                          LC4=tuple(i for i,n in enumerate(nodes) if n['cell_type']=='LC4'),
                          LPLC1=tuple(i for i,n in enumerate(nodes) if n['cell_type']=='LPLC1'),
                          VES041=tuple(circuit.group('VES041')))
            visual_weights=defaultdict(int)
            for pre,post,count in zip(circuit.pre,circuit.post,circuit.signed_counts):
                a,b=nodes[pre],nodes[post]
                if a['cell_type'] in ('LC4','LPLC1','LPLC2') and b['cell_type'] in ('DNp03','DNp06'):
                    visual_weights[f"{a['cell_type']}:{a['side']}->{b['cell_type']}:{b['side']}"]+=int(count)
            metadata = dict(selection='기존 부분 회로 + LC4/LPLC1/DNp03/DNa15/DNb01/VES041 + 하행 세포별 상위 3개 양성 입력',
                            cell_types=dict(Counter(n['cell_type'] for n in nodes)),
                            neurons=len(nodes),connections=len(edges),
                            background_input_nodes=len(background),
                            visual_to_descending_signed_synapses=dict(sorted(visual_weights.items())),
                            external_drive='배경 입력과 감각→VES041 구동은 기능적 가정이며 측정된 시냅스를 추가하지 않음',
                            excluded_counts='확장 후 제외 연결 수는 재계산하지 않음',
                            sha256=hashes)
            _CACHE[key] = circuit,inputs,metadata
        circuit,inputs,metadata = _CACHE[key]
    backend.circuit = circuit
    backend.flight_inputs = inputs
    backend.flight_network = metadata
    backend.hashes = {**backend.hashes,**hashes}
    return backend
