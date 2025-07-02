$(document).ready(function () {
    toastr.options = {
        "closeButton": true,
        "progressBar": true,
        "positionClass": "toast-top-right"
    };

    const recordsTable = $('#recordsTable').DataTable({
        "ajax": { "url": "/api/records", "dataSrc": "data" },
        "columns": [
            { "data": "id" },
            { "data": "patient_id" },
            { "data": "file_name" },
            { "data": "sent_by" },
            { "data": "sent_at" },
            {
                "data": "status",
                "render": function(data, type, row) {
                    let badgeClass = 'bg-secondary';
                    let statusText = data.replace('_', ' ');
                    
                    if (data === 'PENDING_DECRYPTION') badgeClass = 'bg-warning text-dark';
                    else if (data === 'DECRYPTED') badgeClass = 'bg-success';
                    else if (data === 'DECRYPTION_FAILED') {
                        badgeClass = 'bg-danger';
                        // Hiển thị tooltip với lý do thất bại
                        return `<span class="badge ${badgeClass}" 
                                     data-bs-toggle="tooltip" 
                                     title="${row.failure_reason || 'Không rõ lý do'}">
                                    ${statusText}
                                </span>`;
                    }

                    return `<span class="badge ${badgeClass}">${statusText}</span>`;
                }
            },
            {
                "data": null,
                "render": function(data, type, row) {
                    if (row.status === 'PENDING_DECRYPTION' &&
                        typeof userRole !== 'undefined' &&
                        (userRole === 'clerk' || userRole === 'admin')) {
                        return `<button class="btn btn-sm btn-info decrypt-btn"
                                        data-id="${row.id}"
                                        data-info="${row.patient_id}">
                                    Giải mã
                                </button>`;
                    }
                    return '';
                },
                "orderable": false
            }
        ],
        "order": [[0, 'desc']],
        "drawCallback": function(settings) {
            // Kích hoạt lại tất cả các tooltip
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            tooltipTriggerList.map(function(el) {
                return new bootstrap.Tooltip(el);
            });
        }
    });

    // Xử lý gửi hồ sơ
    $('#sendRecordForm').on('submit', function (e) {
        e.preventDefault();
        const sendButton = $('#sendButton');
        const spinner = sendButton.find('.spinner-border');

        sendButton.prop('disabled', true);
        spinner.removeClass('d-none');

        const formData = new FormData(this);

        fetch('/send_record', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                toastr.success(data.message);
                $('#sendRecordForm')[0].reset();
                recordsTable.ajax.reload();
            } else {
                toastr.error(data.message || 'Lỗi không xác định.');
            }
        })
        .catch(error => {
            toastr.error('Lỗi mạng hoặc hệ thống.');
        })
        .finally(() => {
            sendButton.prop('disabled', false);
            spinner.addClass('d-none');
        });
    });

    // Mở modal yêu cầu mật khẩu khi nhấn nút "Giải mã"
    $('#recordsTable tbody').on('click', '.decrypt-btn', function () {
        const recordId = $(this).data('id');
        const patientId = $(this).data('info');

        $('#recordIdToDecrypt').val(recordId);
        $('#modalRecordInfo').text(`BN: ${patientId}`);
        $('#recordsRoomPassword').val('');

        const decryptModal = new bootstrap.Modal(document.getElementById('decryptModal'));
        decryptModal.show();
    });

    // Xác nhận giải mã
    $('#confirmDecryptButton').on('click', function () {
        const recordId = $('#recordIdToDecrypt').val();
        const password = $('#recordsRoomPassword').val();

        if (!password) {
            toastr.warning('Vui lòng nhập mật khẩu.');
            return;
        }

        fetch(`/api/decrypt_record/${recordId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                toastr.success(data.message);
                $('#contentModalTitle').text(`Hồ sơ: ${data.fileName}`);
                $('#decryptedContent').text(data.content);

                const contentModal = new bootstrap.Modal(document.getElementById('contentModal'));
                contentModal.show();

                const decryptModal = bootstrap.Modal.getInstance(document.getElementById('decryptModal'));
                decryptModal.hide();

                recordsTable.ajax.reload();
            } else {
                toastr.error(data.message || 'Giải mã thất bại.');
            }
        })
        .catch(error => {
            toastr.error('Lỗi mạng hoặc hệ thống.');
        });
    });
});
