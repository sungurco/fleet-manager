document.addEventListener('DOMContentLoaded', function () {
    var typeSelect = document.getElementById('id_customer_type');
    var tuzelFields = document.getElementById('tuzelFields');
    var sahisFields = document.getElementById('sahisFields');

    function applyType() {
        var isTuzel = typeSelect.value === 'TUZEL';
        if (tuzelFields) tuzelFields.style.display = isTuzel ? 'block' : 'none';
        if (sahisFields) sahisFields.style.display = isTuzel ? 'none' : 'block';
    }
    if (typeSelect) {
        typeSelect.addEventListener('change', applyType);
        applyType();
    }

    var form = document.getElementById('customerForm');
    if (!form) return;
    var excludeId = form.dataset.customerId || '';
    var checkUrl = form.dataset.checkUrl;

    function wireDuplicateCheck(fieldId, warningId, param, label) {
        var field = document.getElementById(fieldId);
        var warning = document.getElementById(warningId);
        if (!field || !warning) return;
        field.addEventListener('blur', function () {
            var value = field.value.trim();
            warning.classList.remove('show');
            warning.textContent = '';
            if (!value) return;
            var url = checkUrl + '?' + param + '=' + encodeURIComponent(value) + '&exclude=' + encodeURIComponent(excludeId);
            fetch(url)
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.exists) {
                        warning.textContent = 'Bu ' + label + ' ile kayıtlı bir müşteri zaten var: ' + data.name;
                        warning.classList.add('show');
                    }
                })
                .catch(function () {});
        });
    }

    wireDuplicateCheck('id_tc_no', 'tcNoWarning', 'tc_no', 'T.C. Kimlik No');
    wireDuplicateCheck('id_tax_no', 'taxNoWarning', 'tax_no', 'Vergi No');
});
