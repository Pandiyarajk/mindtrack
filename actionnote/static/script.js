/**
 * ActionNote MVP - Frontend JavaScript
 */

// Global utility functions
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast toast-${type} show`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'Not set';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = date - now;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days < 0) {
        return `${Math.abs(days)} days overdue`;
    } else if (days === 0) {
        return 'Today';
    } else if (days === 1) {
        return 'Tomorrow';
    } else if (days < 7) {
        return `In ${days} days`;
    } else {
        return date.toLocaleDateString();
    }
}

// Check if deadline is approaching
function isDeadlineApproaching(dateString, hoursThreshold = 24) {
    if (!dateString) return false;
    
    const deadline = new Date(dateString);
    const now = new Date();
    const diff = deadline - now;
    const hours = diff / (1000 * 60 * 60);
    
    return hours > 0 && hours < hoursThreshold;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('ActionNote initialized');
    
    // Add deadline warnings
    addDeadlineWarnings();
    
    // Auto-save form data (for note form)
    setupAutoSave();
});

// Add visual warnings for approaching deadlines
function addDeadlineWarnings() {
    const taskCards = document.querySelectorAll('.task-card');
    
    taskCards.forEach(card => {
        const metaItems = card.querySelectorAll('.task-meta-item');
        metaItems.forEach(item => {
            if (item.textContent.includes('Deadline:')) {
                const deadlineText = item.textContent.split('Deadline:')[1].trim();
                if (isDeadlineApproaching(deadlineText)) {
                    item.style.color = '#f44336';
                    item.style.fontWeight = 'bold';
                }
            }
        });
    });
}

// Auto-save form data to localStorage
function setupAutoSave() {
    const noteTextArea = document.getElementById('noteText');
    if (!noteTextArea) return;
    
    // Load saved data
    const savedNote = localStorage.getItem('draft_note');
    if (savedNote) {
        noteTextArea.value = savedNote;
        showToast('Draft restored', 'info');
    }
    
    // Save on input
    noteTextArea.addEventListener('input', function() {
        localStorage.setItem('draft_note', this.value);
    });
    
    // Clear on successful submit
    const noteForm = document.getElementById('noteForm');
    if (noteForm) {
        noteForm.addEventListener('submit', function() {
            setTimeout(() => {
                localStorage.removeItem('draft_note');
            }, 1000);
        });
    }
}

// API helper functions
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Task management functions
async function updateTaskStatus(taskId, newStatus) {
    try {
        await apiRequest(`/api/tasks/${taskId}/status`, 'PUT', { status: newStatus });
        showToast(`Task status updated to ${newStatus}`, 'success');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        showToast('Error updating task', 'error');
    }
}

async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note? This cannot be undone.')) {
        return;
    }
    
    try {
        await apiRequest(`/api/notes/${noteId}`, 'DELETE');
        showToast('Note deleted successfully', 'success');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        showToast('Error deleting note', 'error');
    }
}

async function archiveNote(noteId) {
    try {
        await apiRequest(`/api/notes/${noteId}/archive`, 'POST');
        showToast('Note archived successfully', 'success');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        showToast('Error archiving note', 'error');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N: New note
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        window.location.href = '/add_note';
    }
    
    // Ctrl/Cmd + D: Dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        window.location.href = '/dashboard';
    }
});

// Export functions for inline usage
window.updateTaskStatus = updateTaskStatus;
window.deleteNote = deleteNote;
window.archiveNote = archiveNote;
window.showToast = showToast;
