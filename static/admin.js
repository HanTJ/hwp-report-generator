// 관리자 페이지 JavaScript

// 인증 확인
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (!token || !user.is_admin) {
        alert('관리자 권한이 필요합니다.');
        window.location.href = '/login';
        return null;
    }

    // 비밀번호 변경 필요 시 리다이렉트
    if (user.password_reset_required) {
        window.location.href = '/change-password';
        return null;
    }

    // 사용자 정보 표시
    document.getElementById('currentUser').textContent = `${user.username} (관리자)`;

    return token;
}

// 로그아웃
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// 사용자 목록 조회
async function loadUsers() {
    const token = checkAuth();
    if (!token) return;

    try {
        const response = await fetch('/api/admin/users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const users = await response.json();
            displayUsers(users);
        } else {
            document.getElementById('userList').innerHTML = '<p class="error">사용자 목록을 불러오지 못했습니다.</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('userList').innerHTML = '<p class="error">서버 연결에 실패했습니다.</p>';
    }
}

// 사용자 목록 표시
function displayUsers(users) {
    const userListDiv = document.getElementById('userList');

    if (users.length === 0) {
        userListDiv.innerHTML = '<p>등록된 사용자가 없습니다.</p>';
        return;
    }

    let html = '<table class="data-table"><thead><tr>';
    html += '<th>ID</th><th>이메일</th><th>사용자명</th><th>상태</th><th>관리자</th><th>가입일</th><th>액션</th>';
    html += '</tr></thead><tbody>';

    users.forEach(user => {
        const statusBadge = user.is_active
            ? '<span class="badge badge-success">활성</span>'
            : '<span class="badge badge-warning">대기</span>';
        const adminBadge = user.is_admin
            ? '<span class="badge badge-info">관리자</span>'
            : '';
        const createdAt = new Date(user.created_at).toLocaleDateString('ko-KR');

        html += `<tr>
            <td>${user.id}</td>
            <td>${user.email}</td>
            <td>${user.username}</td>
            <td>${statusBadge}</td>
            <td>${adminBadge}</td>
            <td>${createdAt}</td>
            <td class="action-buttons">`;

        if (!user.is_active) {
            html += `<button class="btn btn-small btn-success" onclick="approveUser(${user.id})">승인</button>`;
        } else {
            html += `<button class="btn btn-small btn-warning" onclick="rejectUser(${user.id})">비활성화</button>`;
        }

        html += `<button class="btn btn-small btn-secondary" onclick="resetPassword(${user.id}, '${user.username}')">비밀번호 초기화</button>`;
        html += `</td></tr>`;
    });

    html += '</tbody></table>';
    userListDiv.innerHTML = html;
}

// 사용자 승인
async function approveUser(userId) {
    const token = checkAuth();
    if (!token) return;

    if (!confirm('이 사용자를 승인하시겠습니까?')) return;

    try {
        const response = await fetch(`/api/admin/users/${userId}/approve`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        alert(data.message);

        if (response.ok) {
            loadUsers();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('서버 연결에 실패했습니다.');
    }
}

// 사용자 비활성화
async function rejectUser(userId) {
    const token = checkAuth();
    if (!token) return;

    if (!confirm('이 사용자를 비활성화하시겠습니까?')) return;

    try {
        const response = await fetch(`/api/admin/users/${userId}/reject`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        alert(data.message);

        if (response.ok) {
            loadUsers();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('서버 연결에 실패했습니다.');
    }
}

// 비밀번호 초기화
async function resetPassword(userId, username) {
    const token = checkAuth();
    if (!token) return;

    if (!confirm(`${username}의 비밀번호를 초기화하시겠습니까?`)) return;

    try {
        const response = await fetch(`/api/admin/users/${userId}/reset-password`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(`${data.message}\n\n임시 비밀번호: ${data.temporary_password}\n\n이 비밀번호를 사용자에게 안전하게 전달해주세요.`);
        } else {
            alert(data.detail || '비밀번호 초기화에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('서버 연결에 실패했습니다.');
    }
}

// 토큰 사용량 통계 조회
async function loadTokenStats() {
    const token = checkAuth();
    if (!token) return;

    try {
        const response = await fetch('/api/admin/token-usage', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const stats = await response.json();
            displayTokenStats(stats);
        } else {
            document.getElementById('tokenStats').innerHTML = '<p class="error">통계를 불러오지 못했습니다.</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('tokenStats').innerHTML = '<p class="error">서버 연결에 실패했습니다.</p>';
    }
}

// 토큰 사용량 통계 표시
function displayTokenStats(stats) {
    const statsDiv = document.getElementById('tokenStats');

    if (stats.length === 0) {
        statsDiv.innerHTML = '<p>토큰 사용 내역이 없습니다.</p>';
        return;
    }

    let html = '<table class="data-table"><thead><tr>';
    html += '<th>사용자</th><th>이메일</th><th>입력 토큰</th><th>출력 토큰</th><th>총 토큰</th><th>보고서 수</th><th>최근 사용</th>';
    html += '</tr></thead><tbody>';

    stats.forEach(stat => {
        const lastUsage = stat.last_usage
            ? new Date(stat.last_usage).toLocaleString('ko-KR')
            : '-';

        html += `<tr>
            <td>${stat.username}</td>
            <td>${stat.email}</td>
            <td>${stat.total_input_tokens.toLocaleString()}</td>
            <td>${stat.total_output_tokens.toLocaleString()}</td>
            <td><strong>${stat.total_tokens.toLocaleString()}</strong></td>
            <td>${stat.report_count}</td>
            <td>${lastUsage}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    statsDiv.innerHTML = html;
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadTokenStats();
});
