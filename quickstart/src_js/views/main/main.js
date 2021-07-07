import 'main/index.scss';


export function vt() {
    var list = [];
    list.push('div');
    list = loop(list, 0, 10, 2)
    list = loop(list, 10, 20, 5)
    list = loop(list, 20, 21, 5)
    list = loop(list, 30, 40, 1)

    return list;
}

function loop(list, asdu1, asdu2, io) {
    for (let i = asdu1; i < asdu2; i++) {
        for (let j = 0; j < io; j++) {
            list.push(['div', `ASDU=${i.toString()}, IO=${j.toString()}, 
                        VALUE=${r.get('remote', 'adapter', 'el' + i + "-" + j)}`]);
        }
    }
    return list;
}