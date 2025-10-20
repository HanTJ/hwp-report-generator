// 인증 확인
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (!token) {
        window.location.href = '/login';
        return null;
    }

    // 비밀번호 변경 필요 시 리다이렉트
    if (user.password_reset_required && window.location.pathname !== '/change-password') {
        window.location.href = '/change-password';
        return null;
    }

    // 사용자 정보 표시
    if (document.getElementById('currentUser')) {
        const adminLink = user.is_admin ? ' | <a href="/admin">관리자 페이지</a>' : '';
        document.getElementById('currentUser').innerHTML = `${user.username}${adminLink}`;
    }

    return token;
}

// 로그아웃
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// DOM 요소
const reportForm = document.getElementById('reportForm');
const topicInput = document.getElementById('topic');
const generateBtn = document.getElementById('generateBtn');
const resultDiv = document.getElementById('result');
const reportList = document.getElementById('reportList');
const refreshBtn = document.getElementById('refreshBtn');

// 초기 로드 시 인증 확인 및 보고서 목록 가져오기
document.addEventListener('DOMContentLoaded', () => {
    const token = checkAuth();
    if (token) {
        loadReportList();
    }
});

// 보고서 생성 폼 제출
reportForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const topic = topicInput.value.trim();

    if (topic.length < 3) {
        showResult('보고서 주제는 최소 3자 이상이어야 합니다.', 'error');
        return;
    }

    // 버튼 상태 변경
    setButtonLoading(true);
    hideResult();

    const token = checkAuth();
    if (!token) return;

    try {
        const response = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ topic }),
        });

        const data = await response.json();

        if (response.ok) {
            showResult(
                `보고서가 성공적으로 생성되었습니다!`,
                'success',
                data.id,
                data.filename
            );

            // 폼 초기화
            reportForm.reset();

            // 보고서 목록 새로고침
            setTimeout(() => loadReportList(), 500);
        } else {
            showResult(
                data.detail || '보고서 생성 중 오류가 발생했습니다.',
                'error'
            );
        }
    } catch (error) {
        console.error('Error:', error);
        showResult(
            '서버와의 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
            'error'
        );
    } finally {
        setButtonLoading(false);
    }
});

// 새로고침 버튼 클릭
refreshBtn.addEventListener('click', () => {
    loadReportList();
});

// 버튼 로딩 상태 설정
function setButtonLoading(isLoading) {
    const btnText = generateBtn.querySelector('.btn-text');
    const spinner = generateBtn.querySelector('.spinner');

    if (isLoading) {
        generateBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline';
    } else {
        generateBtn.disabled = false;
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// 결과 메시지 표시
function showResult(message, type, reportId = null, filename = null) {
    resultDiv.className = `result ${type}`;

    let html = `<strong>${type === 'success' ? '✅ 성공' : '❌ 오류'}</strong><p>${message}</p>`;

    if (reportId && filename) {
        html += `<button class="download-link" onclick="downloadReport(${reportId}, '${filename}')">📥 ${filename} 다운로드</button>`;
    }

    resultDiv.innerHTML = html;
    resultDiv.style.display = 'block';
}

// 결과 메시지 숨기기
function hideResult() {
    resultDiv.style.display = 'none';
}

// 보고서 목록 로드
async function loadReportList() {
    const token = checkAuth();
    if (!token) return;

    reportList.innerHTML = '<p class="loading">보고서 목록을 불러오는 중...</p>';

    try {
        const response = await fetch('/api/reports/my-reports', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();

        if (response.ok) {
            displayReportList(data.reports);
        } else {
            reportList.innerHTML = '<p class="empty">보고서 목록을 불러올 수 없습니다.</p>';
        }
    } catch (error) {
        console.error('Error loading reports:', error);
        reportList.innerHTML = '<p class="empty">보고서 목록을 불러오는 중 오류가 발생했습니다.</p>';
    }
}

// 보고서 목록 표시
function displayReportList(reports) {
    if (!reports || reports.length === 0) {
        reportList.innerHTML = '<p class="empty">생성된 보고서가 없습니다.</p>';
        return;
    }

    reportList.innerHTML = reports.map(report => `
        <div class="report-item">
            <div class="report-info">
                <div class="report-name">📄 ${report.title || report.topic}</div>
                <div class="report-meta">
                    파일: ${report.filename} | 크기: ${formatFileSize(report.file_size)} |
                    생성일: ${formatDateString(report.created_at)}
                </div>
            </div>
            <div class="report-actions">
                <button class="btn-small btn-download" onclick="downloadReport(${report.id}, '${report.filename}')">
                    다운로드
                </button>
            </div>
        </div>
    `).join('');
}

// 보고서 다운로드 함수
async function downloadReport(reportId, filename) {
    const token = checkAuth();
    if (!token) return;

    try {
        const response = await fetch(`/api/reports/download/${reportId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            alert(error.detail || '다운로드에 실패했습니다.');
            return;
        }

        // Blob으로 변환하여 다운로드
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Download error:', error);
        alert('다운로드 중 오류가 발생했습니다.');
    }
}

// 파일 크기 포맷팅
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// 날짜 포맷팅
function formatDateString(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}
