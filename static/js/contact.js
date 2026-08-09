document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();

    if (!this.checkValidity()) {
        this.classList.add('was-validated');
        return;
    }

    this.classList.remove('was-validated');

    const form = this;
    const labels = form.dataset;
    const arrowClass = document.documentElement.getAttribute('dir') === 'rtl'
        ? 'bi-arrow-left'
        : 'bi-arrow-right';

    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        message: document.getElementById('message').value
    };

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>${labels.sendingLabel || 'Sending...'}`;

    fetch('/api/contact/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        const alertContainer = document.getElementById('alertContainer');
        const closeLabel = labels.closeLabel || 'Close';

        if (data.success) {
            alertContainer.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="${closeLabel}"></button>
                </div>
            `;
            form.reset();
        } else {
            let errorMessage = data.message || labels.errorPrefix || 'Please fix the following errors:';
            if (data.errors) {
                errorMessage += '<br>';
                for (const errors of Object.values(data.errors)) {
                    errorMessage += `${errors.join(', ')}<br>`;
                }
            }
            alertContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    ${errorMessage}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="${closeLabel}"></button>
                </div>
            `;
        }
    })
    .catch(() => {
        const alertContainer = document.getElementById('alertContainer');
        const closeLabel = labels.closeLabel || 'Close';
        alertContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${labels.genericError || 'An error occurred. Please try again.'}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="${closeLabel}"></button>
            </div>
        `;
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `${labels.submitLabel || 'Send Message'} <i class="bi ${arrowClass} ms-2"></i>`;
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
