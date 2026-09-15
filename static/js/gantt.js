document.addEventListener('DOMContentLoaded', function () {
    var tableView = document.getElementById('rentalsTableView');
    var calendarView = document.getElementById('rentalsCalendarView');
    var toggleButtons = document.querySelectorAll('.view-toggle button[data-view]');

    function showView(view) {
        toggleButtons.forEach(function (b) {
            b.classList.toggle('active', b.dataset.view === view);
        });
        if (tableView) tableView.style.display = view === 'calendar' ? 'none' : 'block';
        if (calendarView) calendarView.style.display = view === 'calendar' ? 'block' : 'none';
    }

    toggleButtons.forEach(function (btn) {
        btn.addEventListener('click', function () { showView(btn.dataset.view); });
    });

    var params = new URLSearchParams(window.location.search);
    if (params.get('view') === 'calendar') showView('calendar');

    // Slide-over preview
    var backdrop = document.getElementById('slideoverBackdrop');
    var panel = document.getElementById('slideoverPanel');
    var body = document.getElementById('slideoverBody');
    var detailLink = document.getElementById('slideoverDetailLink');
    var closeBtn = document.getElementById('slideoverCloseBtn');

    function row(label, value) {
        return '<div class="slideover-row"><span>' + label + '</span><span>' + value + '</span></div>';
    }

    function openSlideover(el) {
        var d = el.dataset;
        body.innerHTML =
            row('Kiralama No', d.rentalNo) +
            row('Araç', d.plate + ' — ' + d.vehicle) +
            row('Müşteri', d.customer) +
            row('Tarih Aralığı', d.start + ' - ' + d.end + ' (' + d.days + ' gün)') +
            row('Toplam Tutar', d.price + ' TL') +
            row('Durum', d.status) +
            row('Ödeme', d.payment);
        detailLink.href = d.detailUrl;
        backdrop.classList.add('show');
        panel.classList.add('show');
    }

    function closeSlideover() {
        backdrop.classList.remove('show');
        panel.classList.remove('show');
    }

    document.querySelectorAll('.gantt-bar').forEach(function (bar) {
        bar.addEventListener('click', function () { openSlideover(bar); });
    });
    if (backdrop) backdrop.addEventListener('click', closeSlideover);
    if (closeBtn) closeBtn.addEventListener('click', closeSlideover);
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeSlideover();
    });
});
