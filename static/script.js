// DOM 요소
const reportForm = document.getElementById('reportForm');
const topicInput = document.getElementById('topic');
const generateBtn = document.getElementById('generateBtn');
const resultDiv = document.getElementById('result');
const reportList = document.getElementById('reportList');
const refreshBtn = document.getElementById('refreshBtn');

// 초기 로드 시 보고서 목록 가져오기
document.addEventListener('DOMContentLoaded', () => {
    loadReportList();
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

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showResult(
                `보고서가 성공적으로 생성되었습니다!`,
                'success',
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
function showResult(message, type, filename = null) {
    resultDiv.className = `result ${type}`;

    let html = `<strong>${type === 'success' ? '✅ 성공' : '❌ 오류'}</strong><p>${message}</p>`;

    if (filename) {
        html += `<a href="/api/download/${filename}" class="download-link" download>📥 ${filename} 다운로드</a>`;
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
    reportList.innerHTML = '<p class="loading">보고서 목록을 불러오는 중...</p>';

    try {
        const response = await fetch('/api/reports');
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
                <div class="report-name">📄 ${report.filename}</div>
                <div class="report-meta">
                    크기: ${formatFileSize(report.size)} |
                    생성일: ${formatDate(report.created)}
                </div>
            </div>
            <div class="report-actions">
                <a href="/api/download/${report.filename}" class="btn-small btn-download" download>
                    다운로드
                </a>
            </div>
        </div>
    `).join('');
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
function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}
