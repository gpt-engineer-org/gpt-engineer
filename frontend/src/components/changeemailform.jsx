import React, { useState } from 'react';

const ChangeEmailForm = ({ userId }) => {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            const response = await fetch('/api/user/change-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    new_email: newEmail,
                    current_password: currentPassword
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message);
                setNewEmail('');
                setCurrentPassword('');
            } else {
                setMessage(data.error);
            }
        } catch (error) {
            setMessage('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="change-email-form">
            <h3>Change Email Address</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>New Email Address</label>
                    <input
                        type="email"
                        value={newEmail}
                        onChange={(e) => setNewEmail(e.target.value)}
                        required
                        placeholder="Enter new email address"
                    />
                </div>
                
                <div className="form-group">
                    <label>Current Password</label>
                    <input
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        required
                        placeholder="Enter your current password"
                    />
                </div>
                
                <button 
                    type="submit" 
                    disabled={loading}
                    className="btn btn-primary"
                >
                    {loading ? 'Sending Verification...' : 'Change Email'}
                </button>
                
                {message && (
                    <div className={`alert ${message.includes('error') ? 'alert-error' : 'alert-success'}`}>
                        {message}
                    </div>
                )}
            </form>
            
            <div className="email-change-info">
                <p><strong>How it works:</strong></p>
                <ol>
                    <li>Enter your new email address and current password</li>
                    <li>We'll send a verification link to your new email</li>
                    <li>Click the link to verify and complete the change</li>
                    <li>You'll receive notifications on both old and new emails</li>
                </ol>
            </div>
        </div>
    );
};

export default ChangeEmailForm;