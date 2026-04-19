const sidebar = document.getElementById('sidebar');
const topbarToggle = document.getElementById('topbarToggle');
const sidebarToggle = document.getElementById('sidebarToggle');

if (topbarToggle) {
    topbarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

async function deleteStock(guildId, serviceName) {
    if (!confirm(`Delete all stock for "${serviceName}"? This cannot be undone.`)) return;
    try {
        const res = await fetch(`/api/guild/${guildId}/stock/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service_name: serviceName })
        });
        const data = await res.json();
        if (data.success) {
            location.reload();
        } else {
            alert('Failed to delete stock');
        }
    } catch (e) {
        alert('Error deleting stock');
    }
}

async function toggleBlacklist(guildId, userId, status) {
    try {
        const res = await fetch(`/api/guild/${guildId}/users/blacklist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, status: status })
        });
        const data = await res.json();
        if (data.success) {
            location.reload();
        } else {
            alert('Failed to update blacklist');
        }
    } catch (e) {
        alert('Error updating blacklist');
    }
}

async function saveSettings(guildId) {
    const genChannels = document.getElementById('genChannels').value
        .split(',').map(x => x.trim()).filter(x => x !== '');
    const premiumChannels = document.getElementById('premiumChannels').value
        .split(',').map(x => x.trim()).filter(x => x !== '');
    const suggestionsChannel = document.getElementById('suggestionsChannel').value.trim() || null;
    const reviewChannel = document.getElementById('reviewChannel').value.trim() || null;

    try {
        const res = await fetch(`/api/guild/${guildId}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'gen-channels': genChannels,
                'premium-gen-channels': premiumChannels,
                'suggestions-channel-id': suggestionsChannel,
                'review-channel-id': reviewChannel
            })
        });
        const data = await res.json();
        if (data.success) {
            alert('✅ Channel settings saved!');
            location.reload();
        }
    } catch (e) {
        alert('Error saving settings');
    }
}

async function saveRoles(guildId) {
    const adminRoles = document.getElementById('adminRoles').value
        .split(',').map(x => x.trim()).filter(x => x !== '');

    try {
        const res = await fetch(`/api/guild/${guildId}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'admin-roles': adminRoles })
        });
        const data = await res.json();
        if (data.success) {
            alert('✅ Role settings saved!');
            location.reload();
        }
    } catch (e) {
        alert('Error saving roles');
    }
}

function searchUsers() {
    const input = document.getElementById('userSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#usersTable tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(input) ? '' : 'none';
    });
}

