document.addEventListener('DOMContentLoaded', function () {
    var statusSelect = document.getElementById('id_status');
    var serviceEndField = document.getElementById('id_estimated_service_end_date');
    var resolutionField = document.getElementById('id_estimated_resolution_date');
    if (!statusSelect) return;

    function wrapperOf(field) {
        return field ? field.closest('p') || field.closest('.mb-3') : null;
    }

    var serviceWrapper = wrapperOf(serviceEndField);
    var resolutionWrapper = wrapperOf(resolutionField);

    function applyVisibility() {
        var status = statusSelect.value;
        if (serviceWrapper) serviceWrapper.style.display = status === 'SERVISTE' ? '' : 'none';
        if (resolutionWrapper) resolutionWrapper.style.display = status === 'HASARLI' ? '' : 'none';
    }

    statusSelect.addEventListener('change', applyVisibility);
    applyVisibility();
});
