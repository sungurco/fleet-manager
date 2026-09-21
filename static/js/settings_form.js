document.addEventListener('DOMContentLoaded', function () {
    function formatDisplayMoney(n) {
        return n.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function parseMoneyValue(str) {
        if (!str) return 0;
        var normalized = String(str).replace(/\./g, '').replace(',', '.');
        var n = parseFloat(normalized);
        return isNaN(n) ? 0 : n;
    }

    function attachMoneyFormatting(input) {
        input.addEventListener('input', function () {
            var raw = input.value.replace(/[^0-9,]/g, '');
            var parts = raw.split(',');
            var intPart = parts[0].replace(/^0+(?=\d)/, '');
            var decPart = parts.length > 1 ? ',' + parts[1].slice(0, 2) : (raw.indexOf(',') !== -1 ? ',' : '');
            intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            input.value = intPart + decPart;
        });
    }

    var moneyInputs = document.querySelectorAll('.money-input');
    moneyInputs.forEach(function (input) {
        var raw = input.value.trim();
        if (raw) {
            var n = parseFloat(raw.replace(',', '.'));
            if (!isNaN(n)) input.value = formatDisplayMoney(n);
        }
    });
    moneyInputs.forEach(attachMoneyFormatting);

    var form = moneyInputs.length ? moneyInputs[0].closest('form') : null;
    if (form) {
        form.addEventListener('submit', function () {
            moneyInputs.forEach(function (input) {
                if (!input.value.trim()) return;
                input.value = parseMoneyValue(input.value).toFixed(2);
            });
        });
    }
});
