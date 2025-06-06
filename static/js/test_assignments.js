// Test Assignments page JavaScript

function deleteAssignment(assignmentId) {
    if (confirm('Ви впевнені, що хочете видалити це призначення?')) {
        // Get CSRF token from meta tag or form
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        fetch(`/admin/test_assignments/${assignmentId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Сталася помилка при видаленні призначення');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Сталася помилка при видаленні призначення');
        });
    }
} 