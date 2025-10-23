// Department Management Functions for Admin Dashboard

let currentSection = 'dashboard';

// Modal functions
function openAddDepartmentModal() {
    const modal = document.getElementById('add-department-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeAddDepartmentModal() {
    const modal = document.getElementById('add-department-modal');
    if (modal) {
        modal.classList.remove('active');
    }
    const form = document.getElementById('add-department-form');
    if (form) {
        form.reset();
    }
}

async function loadDepartments() {
    try {
        const response = await fetch('/api/departments');
        const data = await response.json();
        
        const tbody = document.getElementById('departments-tbody');
        const emptyState = document.getElementById('dept-empty-state');
        
        if (!tbody || !emptyState) return;
        
        if (data.departments && data.departments.length > 0) {
            tbody.innerHTML = '';
            emptyState.style.display = 'none';
            
            data.departments.forEach(dept => {
                const row = document.createElement('tr');
                const categories = Array.isArray(dept.categories) && dept.categories.length > 0 
                    ? dept.categories.join(', ') 
                    : 'N/A';
                const createdDate = dept.created_at 
                    ? new Date(dept.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                    : 'N/A';
                const contact = dept.phone || 'N/A';
                
                row.innerHTML = `
                    <td>${dept.name}</td>
                    <td>${dept.email}</td>
                    <td>${categories}</td>
                    <td>${contact}</td>
                    <td>${createdDate}</td>
                    <td>
                        <div class="action-buttons">
                            <div class="action-btn edit-btn" onclick="viewDepartmentProfile('${dept.id}')" title="View Profile">
                                <i class="fas fa-eye"></i>
                            </div>
                            <div class="action-btn delete-btn" onclick="deleteDepartment('${dept.id}', '${dept.name.replace(/'/g, "\\'")}')">
                                <i class="fas fa-trash"></i>
                            </div>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '';
            emptyState.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading departments:', error);
        if (window.utils && window.utils.showToast) {
            window.utils.showToast('Failed to load departments', 'error');
        } else {
            alert('Failed to load departments');
        }
    }
}

async function deleteDepartment(deptId, deptName) {
    if (!confirm(`Are you sure you want to delete "${deptName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/departments/${deptId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (window.utils && window.utils.showToast) {
                window.utils.showToast('Department deleted successfully', 'success');
            } else {
                alert('Department deleted successfully');
            }
            loadDepartments();
        } else {
            if (window.utils && window.utils.showToast) {
                window.utils.showToast(data.error || 'Failed to delete department', 'error');
            } else {
                alert(data.error || 'Failed to delete department');
            }
        }
    } catch (error) {
        console.error('Error deleting department:', error);
        if (window.utils && window.utils.showToast) {
            window.utils.showToast('Network error. Please try again.', 'error');
        } else {
            alert('Network error. Please try again.');
        }
    }
}

// Initialize form handler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-department-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const deptName = document.getElementById('dept-name').value;
            const deptEmail = document.getElementById('dept-email').value;
            const deptPassword = document.getElementById('dept-password').value;
            const categoriesInput = document.getElementById('dept-categories').value;
            const deptProfile = document.getElementById('dept-profile').value;
            const deptPhone = document.getElementById('dept-phone').value;
            const deptAddress = document.getElementById('dept-address').value;
            
            const categories = categoriesInput 
                ? categoriesInput.split(',').map(c => c.trim()).filter(c => c) 
                : [];
            
            try {
                const response = await fetch('/api/admin/departments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        dept_name: deptName,
                        email: deptEmail,
                        password: deptPassword,
                        categories: categories,
                        profile: deptProfile,
                        phone: deptPhone,
                        address: deptAddress
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    if (window.utils && window.utils.showToast) {
                        window.utils.showToast('Department created successfully', 'success');
                    } else {
                        alert('Department created successfully');
                    }
                    closeAddDepartmentModal();
                    loadDepartments();
                } else {
                    if (window.utils && window.utils.showToast) {
                        window.utils.showToast(data.error || 'Failed to create department', 'error');
                    } else {
                        alert(data.error || 'Failed to create department');
                    }
                }
            } catch (error) {
                console.error('Error creating department:', error);
                if (window.utils && window.utils.showToast) {
                    window.utils.showToast('Network error. Please try again.', 'error');
                } else {
                    alert('Network error. Please try again.');
                }
            }
        });
    }
});

// Department Profile Functions
let currentDepartmentData = null;

async function viewDepartmentProfile(deptId) {
    try {
        const response = await fetch(`/api/admin/departments/${deptId}`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (response.ok && data.department) {
            const dept = data.department;
            currentDepartmentData = dept;
            
            // Populate profile modal
            document.getElementById('profile-dept-name').textContent = dept.name;
            document.getElementById('profile-name').textContent = dept.name;
            document.getElementById('profile-email').textContent = dept.email;
            document.getElementById('profile-phone').textContent = dept.phone || 'Not provided';
            document.getElementById('profile-address').textContent = dept.address || 'Not provided';
            
            // Display categories
            const categoriesContainer = document.getElementById('profile-categories');
            if (dept.categories && dept.categories.length > 0) {
                categoriesContainer.innerHTML = dept.categories.map(cat => 
                    `<span class="category-badge">${cat}</span>`
                ).join('');
            } else {
                categoriesContainer.innerHTML = '<p style="color: var(--gray);">No categories assigned</p>';
            }
            
            // Display description
            const descriptionBox = document.getElementById('profile-description');
            descriptionBox.textContent = dept.profile || 'No description provided.';
            
            // Load statistics (you can fetch this from backend if needed)
            document.getElementById('profile-total-petitions').textContent = dept.total_petitions || '0';
            document.getElementById('profile-pending-petitions').textContent = dept.pending_petitions || '0';
            document.getElementById('profile-resolved-petitions').textContent = dept.resolved_petitions || '0';
            
            // Show modal
            document.getElementById('department-profile-modal').classList.add('active');
        } else {
            if (window.utils && window.utils.showToast) {
                window.utils.showToast('Failed to load department profile', 'error');
            } else {
                alert('Failed to load department profile');
            }
        }
    } catch (error) {
        console.error('Error loading department profile:', error);
        if (window.utils && window.utils.showToast) {
            window.utils.showToast('Network error. Please try again.', 'error');
        } else {
            alert('Network error. Please try again.');
        }
    }
}

function closeDepartmentProfileModal() {
    document.getElementById('department-profile-modal').classList.remove('active');
    currentDepartmentData = null;
}

function editDepartmentProfile() {
    if (!currentDepartmentData) return;
    
    // Close profile modal
    closeDepartmentProfileModal();
    
    // Populate edit form
    document.getElementById('edit-dept-id').value = currentDepartmentData.id;
    document.getElementById('edit-dept-name').value = currentDepartmentData.name;
    document.getElementById('edit-dept-email').value = currentDepartmentData.email;
    document.getElementById('edit-dept-categories').value = currentDepartmentData.categories ? currentDepartmentData.categories.join(', ') : '';
    document.getElementById('edit-dept-profile').value = currentDepartmentData.profile || '';
    document.getElementById('edit-dept-phone').value = currentDepartmentData.phone || '';
    document.getElementById('edit-dept-address').value = currentDepartmentData.address || '';
    
    // Show edit modal
    document.getElementById('edit-department-modal').classList.add('active');
}

function closeEditDepartmentModal() {
    document.getElementById('edit-department-modal').classList.remove('active');
    document.getElementById('edit-department-form').reset();
}

// Initialize edit form handler
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('edit-department-form');
    if (editForm) {
        editForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const deptId = document.getElementById('edit-dept-id').value;
            const deptName = document.getElementById('edit-dept-name').value;
            const deptEmail = document.getElementById('edit-dept-email').value;
            const categoriesInput = document.getElementById('edit-dept-categories').value;
            const deptProfile = document.getElementById('edit-dept-profile').value;
            const deptPhone = document.getElementById('edit-dept-phone').value;
            const deptAddress = document.getElementById('edit-dept-address').value;
            
            const categories = categoriesInput 
                ? categoriesInput.split(',').map(c => c.trim()).filter(c => c) 
                : [];
            
            try {
                const response = await fetch(`/api/admin/departments/${deptId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        name: deptName,
                        email: deptEmail,
                        categories: categories,
                        profile: deptProfile,
                        phone: deptPhone,
                        address: deptAddress
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    if (window.utils && window.utils.showToast) {
                        window.utils.showToast('Department profile updated successfully', 'success');
                    } else {
                        alert('Department profile updated successfully');
                    }
                    closeEditDepartmentModal();
                    loadDepartments();
                } else {
                    if (window.utils && window.utils.showToast) {
                        window.utils.showToast(data.error || 'Failed to update department', 'error');
                    } else {
                        alert(data.error || 'Failed to update department');
                    }
                }
            } catch (error) {
                console.error('Error updating department:', error);
                if (window.utils && window.utils.showToast) {
                    window.utils.showToast('Network error. Please try again.', 'error');
                } else {
                    alert('Network error. Please try again.');
                }
            }
        });
    }
});
