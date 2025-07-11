// Great British Beer - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    initializeFormValidation();

    // Handle like buttons (AJAX)
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const reviewId = this.dataset.reviewId;
            const likeIcon = this.querySelector('i');
            const likeCount = this.querySelector('.like-count');
            
            // Add loading state
            const originalIcon = likeIcon.className;
            likeIcon.className = 'bi bi-heart loading';
            
            fetch(`/reviews/like/${reviewId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                // Update UI based on response
                if (data.liked) {
                    this.classList.add('liked');
                    likeIcon.className = 'bi bi-heart-fill';
                } else {
                    this.classList.remove('liked');
                    likeIcon.className = 'bi bi-heart';
                }
                
                // Update like count
                if (likeCount) {
                    likeCount.textContent = data.like_count;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Restore original icon on error
                likeIcon.className = originalIcon;
            });
        });
    });

    // Newsletter signup form
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Show loading state
            submitBtn.textContent = 'Subscribing...';
            submitBtn.disabled = true;
            
            // Simulate API call (replace with actual endpoint)
            setTimeout(() => {
                submitBtn.textContent = 'Subscribed!';
                submitBtn.classList.remove('btn-warning');
                submitBtn.classList.add('btn-success');
                
                // Reset form
                this.reset();
                
                // Reset button after 3 seconds
                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('btn-success');
                    submitBtn.classList.add('btn-warning');
                }, 3000);
            }, 1000);
        });
    }

    // Search form enhancements
    const searchForm = document.querySelector('form[action*="beer_list"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="search"]');
        
        // Add search suggestions (simple implementation)
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Here you could implement search suggestions
                console.log('Searching for:', query);
            }
        });
    }

    // Rating display enhancements
    const ratingElements = document.querySelectorAll('.rating-stars');
    ratingElements.forEach(element => {
        const rating = parseFloat(element.dataset.rating);
        const stars = element.querySelectorAll('i');
        
        stars.forEach((star, index) => {
            if (index < Math.floor(rating)) {
                star.className = 'bi bi-star-fill';
            } else if (index < rating) {
                star.className = 'bi bi-star-half';
            } else {
                star.className = 'bi bi-star';
            }
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Image lazy loading enhancement
    const images = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Utility function to get CSRF token
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

// Social sharing functions
function shareOnTwitter(url, text) {
    const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(twitterUrl, '_blank', 'width=600,height=400');
}

function shareOnFacebook(url) {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(facebookUrl, '_blank', 'width=600,height=400');
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Link copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Link copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy link', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// Toast notification function
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}

/**
 * Initialize comprehensive form validation
 */
function initializeFormValidation() {
    // Password strength validation
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        if (field.name === 'password1' || field.name === 'password') {
            field.addEventListener('input', validatePasswordStrength);
        }
    });

    // Email validation
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        field.addEventListener('blur', validateEmail);
    });

    // Password confirmation validation
    const confirmPasswordField = document.querySelector('input[name="password2"]');
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', validatePasswordConfirmation);
    }

    // Real-time form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

/**
 * Validate password strength
 */
function validatePasswordStrength(e) {
    const password = e.target.value;
    const feedback = getOrCreateFeedback(e.target, 'password-strength');
    
    if (password.length === 0) {
        clearValidation(e.target, feedback);
        return;
    }

    const strength = calculatePasswordStrength(password);
    
    if (strength.score < 3) {
        setInvalid(e.target, feedback, strength.message);
    } else {
        setValid(e.target, feedback, 'Password strength: ' + strength.level);
    }
}

/**
 * Calculate password strength
 */
function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];

    // Length check
    if (password.length >= 8) score++;
    else feedback.push('at least 8 characters');

    // Uppercase check
    if (/[A-Z]/.test(password)) score++;
    else feedback.push('uppercase letter');

    // Lowercase check
    if (/[a-z]/.test(password)) score++;
    else feedback.push('lowercase letter');

    // Number check
    if (/\d/.test(password)) score++;
    else feedback.push('number');

    // Special character check
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;
    else feedback.push('special character');

    const levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const level = levels[Math.min(score, 4)];
    
    const message = score < 3 ? 
        `Password needs: ${feedback.join(', ')}` : 
        `Strong password`;

    return { score, level, message };
}

/**
 * Validate email format
 */
function validateEmail(e) {
    const email = e.target.value;
    const feedback = getOrCreateFeedback(e.target, 'email-validation');
    
    if (email.length === 0) {
        clearValidation(e.target, feedback);
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
        setInvalid(e.target, feedback, 'Please enter a valid email address');
    } else {
        setValid(e.target, feedback, 'Valid email address');
    }
}

/**
 * Validate password confirmation
 */
function validatePasswordConfirmation(e) {
    const confirmPassword = e.target.value;
    const passwordField = document.querySelector('input[name="password1"]') || 
                         document.querySelector('input[name="password"]');
    const feedback = getOrCreateFeedback(e.target, 'password-confirmation');
    
    if (confirmPassword.length === 0) {
        clearValidation(e.target, feedback);
        return;
    }

    if (!passwordField || confirmPassword !== passwordField.value) {
        setInvalid(e.target, feedback, 'Passwords do not match');
    } else {
        setValid(e.target, feedback, 'Passwords match');
    }
}

/**
 * Validate entire form
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            const feedback = getOrCreateFeedback(field, 'required-validation');
            setInvalid(field, feedback, 'This field is required');
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Get or create feedback element
 */
function getOrCreateFeedback(field, className) {
    let feedback = field.parentNode.querySelector(`.${className}`);
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = `invalid-feedback ${className}`;
        field.parentNode.appendChild(feedback);
    }
    return feedback;
}

/**
 * Set field as invalid
 */
function setInvalid(field, feedback, message) {
    field.classList.remove('is-valid');
    field.classList.add('is-invalid');
    feedback.textContent = message;
    feedback.style.display = 'block';
}

/**
 * Set field as valid
 */
function setValid(field, feedback, message) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    feedback.textContent = message;
    feedback.className = feedback.className.replace('invalid-feedback', 'valid-feedback');
    feedback.style.display = 'block';
}

/**
 * Clear validation state
 */
function clearValidation(field, feedback) {
    field.classList.remove('is-valid', 'is-invalid');
    feedback.style.display = 'none';
}
