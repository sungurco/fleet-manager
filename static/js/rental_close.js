document.addEventListener('DOMContentLoaded', function () {
    var DATA = window.RENTAL_CLOSE_DATA || {};

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

    var form = document.getElementById('rentalCloseForm');
    if (form) {
        form.addEventListener('submit', function () {
            moneyInputs.forEach(function (input) {
                if (!input.value.trim()) return;
                input.value = parseMoneyValue(input.value).toFixed(2);
            });
        });
    }

    var actualEndInput = document.getElementById('id_actual_end_date');
    var totalInput = document.getElementById('id_new_total_price');
    var summaryBox = document.getElementById('closeSummary');
    var dailyPrice = parseFloat(DATA.dailyPrice) || 0;
    var plannedDays = DATA.plannedDays || 0;
    var plannedTotal = parseFloat(DATA.plannedTotal) || 0;
    var startDate = DATA.startDate ? new Date(DATA.startDate) : null;
    var totalUserEdited = false;

    function updateSummary() {
        if (!actualEndInput || !actualEndInput.value || !startDate || !summaryBox) return;
        var end = new Date(actualEndInput.value);
        var diffDays = Math.max(Math.round((end - startDate) / 86400000), 1);
        var suggested = diffDays * dailyPrice;

        if (!totalUserEdited) {
            totalInput.value = formatDisplayMoney(suggested);
        }

        var entered = parseMoneyValue(totalInput.value);
        var diff = plannedTotal - entered;
        var diffText;
        if (diff > 0.004) {
            diffText = formatDisplayMoney(diff) + ' TL iade edilecek';
        } else if (diff < -0.004) {
            diffText = formatDisplayMoney(Math.abs(diff)) + ' TL ek tahsilat gerekiyor';
        } else {
            diffText = 'Fark yok';
        }

        summaryBox.textContent =
            'Planlanan: ' + plannedDays + ' gün / ' + formatDisplayMoney(plannedTotal) + ' TL — ' +
            'Gerçekleşen: ' + diffDays + ' gün / ' + formatDisplayMoney(entered) + ' TL — ' +
            'Fark: ' + diffText;
    }

    if (actualEndInput && totalInput) {
        actualEndInput.addEventListener('change', updateSummary);
        totalInput.addEventListener('input', function () {
            totalUserEdited = true;
            updateSummary();
        });
        updateSummary();
    }
});
