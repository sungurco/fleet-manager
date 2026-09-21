document.addEventListener('DOMContentLoaded', function () {
    var DATA = window.RENTAL_FORM_DATA || { vehicles: [], customers: [], drivers: [] };

    /* ---------- TR sayı formatlama (2000 -> 2.000, submit'te düz sayıya çevrilir) ---------- */
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
    // Sunucudan gelen ilk değer her zaman düz ondalık formattadır (örn. "2000.00" - Django
    // Decimal render'ı), bunu TR görünümüne ("2.000,00") çevirmeden formatlamaya başlamamalı.
    moneyInputs.forEach(function (input) {
        var raw = input.value.trim();
        if (raw) {
            var n = parseFloat(raw.replace(',', '.'));
            if (!isNaN(n)) input.value = formatDisplayMoney(n);
        }
    });
    moneyInputs.forEach(attachMoneyFormatting);

    var form = document.getElementById('rentalForm');
    if (form) {
        form.addEventListener('submit', function () {
            moneyInputs.forEach(function (input) {
                if (!input.value.trim()) return;
                input.value = parseMoneyValue(input.value).toFixed(2);
            });
        });
    }

    /* ---------- Searchable select (Araç / Müşteri) ---------- */
    function setupSearchable(selectId, inputId, dropdownId, items, renderLabel, renderRow, matchText) {
        matchText = matchText || renderLabel;
        var select = document.getElementById(selectId);
        var input = document.getElementById(inputId);
        var dropdown = document.getElementById(dropdownId);
        if (!select || !input || !dropdown) return null;

        select.style.display = 'none';

        function setValue(item) {
            select.value = item ? item.id : '';
            input.value = item ? renderLabel(item) : '';
            dropdown.classList.remove('show');
            select.dispatchEvent(new Event('change'));
        }

        var initialId = select.value;
        if (initialId) {
            var initialItem = items.find(function (i) { return String(i.id) === String(initialId); });
            if (initialItem) input.value = renderLabel(initialItem);
        }

        function renderDropdown(filtered) {
            dropdown.innerHTML = '';
            if (!filtered.length) {
                var empty = document.createElement('div');
                empty.className = 'searchable-empty';
                empty.textContent = 'Sonuç bulunamadı';
                dropdown.appendChild(empty);
            } else {
                filtered.slice(0, 50).forEach(function (item) {
                    var row = document.createElement('div');
                    row.className = 'searchable-option';
                    row.innerHTML = renderRow(item);
                    row.addEventListener('mousedown', function (e) {
                        e.preventDefault();
                        setValue(item);
                    });
                    dropdown.appendChild(row);
                });
            }
            dropdown.classList.add('show');
        }

        function filterAndRender() {
            var q = input.value.trim().toLowerCase();
            var filtered = !q ? items : items.filter(function (i) { return matchText(i).toLowerCase().indexOf(q) !== -1; });
            renderDropdown(filtered);
        }

        input.addEventListener('focus', filterAndRender);
        input.addEventListener('input', function () {
            if (select.value) select.value = '';
            filterAndRender();
        });
        document.addEventListener('click', function (e) {
            if (e.target !== input && !dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });

        return { setValue: setValue };
    }

    var vehicleItems = (DATA.vehicles || []).slice().sort(function (a, b) {
        if (a.status === 'MUSAIT' && b.status !== 'MUSAIT') return -1;
        if (a.status !== 'MUSAIT' && b.status === 'MUSAIT') return 1;
        return 0;
    });
    setupSearchable('id_vehicle', 'vehicle_search', 'vehicle_dropdown', vehicleItems,
        function (v) { return v.label; },
        function (v) { return '<span>' + v.label + '</span><span class="searchable-tag tag-' + v.status + '">' + v.status_label + '</span>'; }
    );

    setupSearchable('id_customer', 'customer_search', 'customer_dropdown', DATA.customers || [],
        function (c) { return c.label; },
        function (c) { return '<span>' + c.label + '</span><span class="searchable-tag tag-type-' + c.type + '">' + c.type_label + '</span>'; },
        function (c) { return c.search || c.label; }
    );

    /* ---------- Araç durumu bilgilendirme uyarısı (Serviste/Hasarlı — engellemeyen) ---------- */
    var vehicleSelect = document.getElementById('id_vehicle');
    var vehicleStatusWarning = document.getElementById('vehicleStatusWarning');

    function formatTRDate(isoDate) {
        var parts = isoDate.split('-');
        var d = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
        return d.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric', timeZone: 'UTC' });
    }

    function setVehicleWarning(tone, text) {
        vehicleStatusWarning.textContent = text;
        vehicleStatusWarning.classList.remove('info', 'caution', 'danger');
        vehicleStatusWarning.classList.add(tone, 'show');
    }

    function updateVehicleStatusWarning() {
        if (!vehicleSelect || !vehicleStatusWarning) return;
        var vehicle = vehicleItems.find(function (v) { return String(v.id) === String(vehicleSelect.value); });
        vehicleStatusWarning.classList.remove('show', 'info', 'caution', 'danger');
        vehicleStatusWarning.textContent = '';
        if (!vehicle) return;

        if (vehicle.status === 'SERVISTE') {
            var returnDate = vehicle.estimated_service_end_date;
            var startVal = document.getElementById('id_start_date').value;
            if (!returnDate) {
                setVehicleWarning('caution', 'Bu araç şu an Serviste — tahmini dönüş tarihi girilmemiş, işlem yapmadan önce kontrol edin.');
            } else if (startVal && startVal < returnDate) {
                setVehicleWarning('caution', 'Seçtiğiniz başlangıç tarihi (' + formatTRDate(startVal) + '), aracın tahmini dönüş tarihinden (' + formatTRDate(returnDate) + ') önce.');
            } else {
                setVehicleWarning('info', 'Bu araç şu an Serviste — tahmini dönüş: ' + formatTRDate(returnDate));
            }
        } else if (vehicle.status === 'HASARLI') {
            var resolutionDate = vehicle.estimated_resolution_date;
            var message = 'Bu araç Hasarlı olarak işaretli — dönüş tarihi belirsiz olabilir, kiralama oluşturmadan önce aracın durumunu kontrol edin.';
            if (resolutionDate) {
                message += ' Tahmini çözüm tarihi: ' + formatTRDate(resolutionDate) + ' (kesin değildir).';
            }
            setVehicleWarning('danger', message);
        }
    }

    if (vehicleSelect) {
        vehicleSelect.addEventListener('change', updateVehicleStatusWarning);
        updateVehicleStatusWarning();
    }

    /* ---------- Sürücü: seçilen müşteriye göre filtrele + ehliyet uyarısı ---------- */
    var customerSelect = document.getElementById('id_customer');
    var driverSelect = document.getElementById('id_driver');
    var driverWarning = document.getElementById('driverLicenseWarning');
    var allDrivers = (DATA.drivers || []).slice();

    function checkDriverLicense() {
        var opt = driverSelect.options[driverSelect.selectedIndex];
        if (opt && opt.value && opt.dataset.hasLicense === '0') {
            driverWarning.classList.add('show');
        } else {
            driverWarning.classList.remove('show');
        }
    }

    function refreshDriverOptions(keepId) {
        var customerId = customerSelect.value;
        var current = keepId !== undefined ? keepId : driverSelect.value;
        driverSelect.innerHTML = '<option value="">---------</option>';
        allDrivers
            .filter(function (d) { return customerId && String(d.customer_id) === String(customerId); })
            .forEach(function (d) {
                var opt = document.createElement('option');
                opt.value = d.id;
                opt.textContent = d.label;
                opt.dataset.hasLicense = d.has_license ? '1' : '0';
                if (String(d.id) === String(current)) opt.selected = true;
                driverSelect.appendChild(opt);
            });
        checkDriverLicense();
    }

    if (customerSelect && driverSelect) {
        customerSelect.addEventListener('change', function () { refreshDriverOptions(null); });
        driverSelect.addEventListener('change', checkDriverLicense);
        refreshDriverOptions(driverSelect.value);
    }

    /* ---------- Hızlı sürücü ekleme (sayfadan ayrılmadan) ---------- */
    var quickAddToggle = document.getElementById('quickAddDriverToggle');
    var quickAddPanel = document.getElementById('quickAddDriverPanel');
    if (quickAddToggle) {
        quickAddToggle.addEventListener('click', function () {
            quickAddPanel.classList.toggle('show');
        });
    }
    var quickAddSubmit = document.getElementById('quickAddDriverSubmit');
    if (quickAddSubmit) {
        quickAddSubmit.addEventListener('click', function () {
            var errorBox = document.getElementById('quickAddDriverError');
            errorBox.textContent = '';
            var customerId = customerSelect.value;
            if (!customerId) {
                errorBox.textContent = 'Önce müşteri seçmelisiniz.';
                return;
            }
            var name = document.getElementById('quickDriverName').value.trim();
            var tcNo = document.getElementById('quickDriverTc').value.trim();
            var passportNo = document.getElementById('quickDriverPassport').value.trim();
            var licenseNo = document.getElementById('quickDriverLicense').value.trim();
            if (!name) { errorBox.textContent = 'Ad Soyad gerekli.'; return; }
            if (!tcNo && !passportNo) { errorBox.textContent = 'T.C. Kimlik No veya Pasaport No girilmeli.'; return; }

            var formData = new FormData();
            formData.append('full_name', name);
            formData.append('tc_no', tcNo);
            formData.append('passport_no', passportNo);
            formData.append('license_no', licenseNo);
            formData.append('csrfmiddlewaretoken', document.querySelector('#rentalForm [name=csrfmiddlewaretoken]').value);

            fetch('/kiralama/musteriler/' + customerId + '/surucu-ekle-ajax/', { method: 'POST', body: formData })
                .then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
                .then(function (res) {
                    if (!res.ok) {
                        var msgs = [];
                        Object.keys(res.data.errors || {}).forEach(function (k) {
                            res.data.errors[k].forEach(function (e) { msgs.push(e.message); });
                        });
                        errorBox.textContent = msgs.join(' ') || 'Sürücü eklenemedi.';
                        return;
                    }
                    allDrivers.push({ id: res.data.id, customer_id: parseInt(customerId, 10), label: res.data.label, has_license: res.data.has_license });
                    refreshDriverOptions(res.data.id);
                    quickAddPanel.classList.remove('show');
                    ['quickDriverName', 'quickDriverTc', 'quickDriverPassport', 'quickDriverLicense'].forEach(function (id) {
                        document.getElementById(id).value = '';
                    });
                })
                .catch(function () { errorBox.textContent = 'Sürücü eklenirken bir hata oluştu.'; });
        });
    }

    /* ---------- Gün sayısı + tutar hesaplama (sticky özet kutusu) ---------- */
    var startInput = document.getElementById('id_start_date');
    var endInput = document.getElementById('id_end_date');
    var priceInput = document.getElementById('id_daily_price_snapshot');
    var totalInput = document.getElementById('id_total_price');
    var dateWarning = document.getElementById('dateWarning');
    var daysBox = document.getElementById('summaryDays');
    var suggestedBox = document.getElementById('summarySuggested');
    var enteredBox = document.getElementById('summaryEntered');
    var summaryNote = document.getElementById('summaryNote');

    var totalUserEdited = !!(totalInput && totalInput.value && parseMoneyValue(totalInput.value) > 0);

    function computeDays() {
        if (!startInput.value || !endInput.value) {
            dateWarning.classList.remove('show');
            return null;
        }
        var start = new Date(startInput.value);
        var end = new Date(endInput.value);
        var diffDays = Math.round((end - start) / 86400000);
        if (diffDays <= 0) {
            dateWarning.classList.add('show');
            return null;
        }
        dateWarning.classList.remove('show');
        return diffDays;
    }

    function updateSummary() {
        var days = computeDays();
        daysBox.textContent = days ? days + ' gün' : '-';

        var dailyPrice = parseMoneyValue(priceInput.value);
        var suggested = (days && dailyPrice) ? days * dailyPrice : 0;
        suggestedBox.textContent = suggested ? formatDisplayMoney(suggested) + ' TL' : '-';

        if (suggested && !totalUserEdited) {
            totalInput.value = formatDisplayMoney(suggested);
        }

        var enteredTotal = parseMoneyValue(totalInput.value);
        enteredBox.textContent = enteredTotal ? formatDisplayMoney(enteredTotal) + ' TL' : '-';

        if (suggested && enteredTotal && Math.abs(enteredTotal - suggested) > 0.01) {
            summaryNote.textContent = 'Önerilen: ' + formatDisplayMoney(suggested) + ' TL';
            summaryNote.classList.add('show');
        } else {
            summaryNote.classList.remove('show');
        }
    }

    if (startInput && endInput && priceInput && totalInput) {
        startInput.addEventListener('change', function () {
            updateSummary();
            updateVehicleStatusWarning();
        });
        endInput.addEventListener('change', updateSummary);
        priceInput.addEventListener('input', updateSummary);
        totalInput.addEventListener('input', function () {
            totalUserEdited = true;
            updateSummary();
        });
        updateSummary();
    }

    /* ---------- Provizyon: seçilen tipin güncel tutarını bilgi amaçlı göster ---------- */
    var provisionSelect = document.getElementById('id_provision_type');
    var provisionInfo = document.getElementById('provisionInfo');
    var provisionAmounts = DATA.provisionAmounts || {};
    var provisionLabels = { EKONOMIK: 'Ekonomik Sınıf', LUKS: 'Lüks Sınıf' };

    function updateProvisionInfo() {
        if (!provisionSelect || !provisionInfo) return;
        var val = provisionSelect.value;
        if (provisionLabels[val] && provisionAmounts[val] !== undefined) {
            var amount = parseFloat(provisionAmounts[val]) || 0;
            provisionInfo.textContent = provisionLabels[val] + ' — ' + formatDisplayMoney(amount) + ' TL';
        } else {
            provisionInfo.textContent = '';
        }
    }

    if (provisionSelect) {
        provisionSelect.addEventListener('change', updateProvisionInfo);
        updateProvisionInfo();
    }
});
