function opennav() {
    document.getElementById('mainmenu').style.width = '100%';
}

function closenav() {
    document.getElementById('mainmenu').style.width = '0';
}

function formatNumber(x) {
    return x.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}

let quantity = document.getElementById("orderQty");
let price = document.getElementById('price').textContent;
let newprice = price.split(',')
let finalprice = "";
for (i = 0; i < newprice.length; i++) {
    finalprice += newprice[i];
}
finalprice = Number(finalprice)
let result;

function calc() {
    result = Number(quantity.value) * finalprice;
    document.getElementById('qty').textContent = quantity.value;
    document.getElementById('total').textContent = formatNumber(result);
}