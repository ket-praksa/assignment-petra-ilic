import 'main/index.scss';
import * as plotly from 'plotly.js-dist/plotly.js';
import { svg } from './svg.js';


export function vt() {
    window.onclick = function (event) {
        let modal = document.getElementById("graph_modal");
        if (modal != null && event.target == modal) {
            modal.style.display = "none";
        }
    }
    return ['div.main', svg(), tables(), show_graph()];
}

export function plot(data, layout, config) {
    data = data.split(",")

    let pair;
    let tmstps = [];
    let vals = [];
    for (let i = 0; i < data.length; i++) {
        pair = data[i].split(";");
        tmstps.push(pair[0]);
        vals.push(pair[1]);
    }


    let modal = document.getElementById("graph_modal");
    let text = "";
    if (modal != null) {
        text = modal.title;
    }

    layout = {
        autosize: true,
        title: {text: text}
    }

    let format_data = [{
        x: tmstps,
        y: vals,
        type: 'scatter',
    }];

    return ['div.plot', {
        'attrs': {
            'id': 'modal_content'
        },
        plotData: format_data,
        hook: {
            insert: vnode => plotly.newPlot(vnode.elm, format_data, layout, config),
            update: (oldVnode, vnode) => {
                if (u.equals(oldVnode.data.plotData, vnode.data.plotData)) return;
                plotly.react(vnode.elm, format_data, layout, config);
            },
            destroy: vnode => plotly.purge(vnode.elm)
        }
    }];
}

function show_graph() {

    return ['div.modal', {
            'attrs': {
                'id': 'graph_modal'
            }
        },
        [plot(`${r.get('remote', 'db_adapter', 'pairs')}`)]
    ]
}

function tables() {
    let table_div = ['div.table_div'];
    table_div = table(table_div, 0, 7, 2, "BUS", "Aktivna snaga [MW]", "Jalova snaga [MVar]");
    table_div = table(table_div, 10, 14, 5, "LINE", "Aktivna snaga na početku voda [MW]",
        "Jalova snaga na početku voda [MVar]",
        "Aktivna snaga na kraju voda [MW]",
        "Jalova snaga na kraju voda [MVar]",
        "Opterećenje [%]");
    table_div = table(table_div, 30, 38, 1, "SWITCH", "Stanje", "");
    table_div = table(table_div, 20, 21, 5, "TRAFO", "Aktivna snaga na strani s višim naponom [MW]",
        "Jalova snaga na strani s višim naponom [MVar]",
        "Aktivna snaga na strani s nižim naponom [MW]",
        "Jalova snaga na strani s nižim naponom [MVar]",
        "Opterećenje [%]");
    return table_div
}

function table(table_div, asdu1, asdu2, io, ...args) {
    let table = ['table'];
    let header = ['tr'];
    for (let i = 0; i < args.length; i++) {
        header.push(['th', args[i]]);
    }
    table.push(header);
    table = get_values(table, asdu1, asdu2, io, args);

    table_div.push(table);
    return table_div
}

function get_values(list, asdu1, asdu2, io, args) {

    for (let i = asdu1; i < asdu2; i++) {
        let ct = i;
        if (asdu1 != 0)
            ct = i % asdu1

        let row = ['tr', ['td', `${(ct).toString()}`]]

        for (let j = 0; j < io; j++) {

            let id = 'el' + i + "-" + j;
            let val = `${r.get('remote', 'adapter', id)}`;

            row.push(['td.value', {
                on: {
                    click: () => graph(i, j, args[0], args[1+j], ct)
                },
                'attrs': {
                    'id': id,
                    'href': "#modal_content",
                    'title': "Show graph",
                }
            }, val]);

            if (asdu1 >= 30 && asdu2 <= 39) {
                let checked = false;
                if (val == '1')
                    checked = true;

                update_switch(ct, checked)
                row = toggle_button(row, checked, i, j)
            }
        }
        list.push(row);
    }
    return list;
}

function toggle(asdu, io) {
    let values = {0: "OFF", 1: "ON"};
    let val = document.getElementById('el' + asdu + '-' + io).textContent;
    let new_val;
    new_val = 1 - val
    hat.conn.send('adapter', {'value': values[new_val], 'asdu': asdu, 'io': 0,})
}

function update_switch(ct, checked) {
    let el = document.getElementById("sw" + ct);
    if (el != null) {
        let value = el.getAttribute("d");
        value = value.split(" ");
        value[5] = value[2];
        if (!checked)
            value[5] -= 10;
        el.setAttribute('d', value.join(" "))
    }
}

function toggle_button(row, checked, asdu, io) {
    row.push(['td', [
        ['label.switch',
            ['input', {
                on: {
                    change: () => toggle(asdu, io)
                },
                'attrs': {
                    'type': 'checkbox',
                    'checked': checked
                }
            }],
            ['span.slider round']
        ]
    ]]);
    return row;
}

function graph(asdu, io, element, name, ct) {
    hat.conn.send('db_adapter', {
        'asdu': asdu.toString(),
        'io': io.toString(),
    })

    let modal = document.getElementById("graph_modal");
    if (modal != null) {
        modal.style.display = "block";
        modal.title = element + " " + ct.toString() + ": " + name;   
    }
}