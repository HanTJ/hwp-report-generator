// 인증 관련 JavaScript

// 로그인 폼 처리
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const resultDiv = document.getElementById("result");

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      alert("token" + data.access_token);

      if (response.ok) {
        // 토큰 저장
        console.log("access_token", data.access_token);
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));

        // 비밀번호 변경이 필요한 경우
        if (data.user.password_reset_required) {
          resultDiv.className = "result success";
          resultDiv.textContent = "로그인 성공! 비밀번호를 변경해야 합니다...";
          resultDiv.style.display = "block";

          // 비밀번호 변경 페이지로 이동
          setTimeout(() => {
            window.location.href = "/change-password";
          }, 1000);
        } else {
          resultDiv.className = "result success";
          resultDiv.textContent = "로그인 성공! 메인 페이지로 이동합니다...";
          resultDiv.style.display = "block";

          // 메인 페이지로 이동
          setTimeout(() => {
            window.location.href = "/";
          }, 1000);
        }
      } else {
        resultDiv.className = "result error";
        resultDiv.textContent = data.detail || "로그인에 실패했습니다.";
        resultDiv.style.display = "block";
      }
    } catch (error) {
      console.error("Error:", error);
      resultDiv.className = "result error";
      resultDiv.textContent = "서버 연결에 실패했습니다.";
      resultDiv.style.display = "block";
    }
  });
}

// 회원가입 폼 처리
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const resultDiv = document.getElementById("result");

    // 비밀번호 확인
    if (password !== confirmPassword) {
      resultDiv.className = "result error";
      resultDiv.textContent = "비밀번호가 일치하지 않습니다.";
      resultDiv.style.display = "block";
      return;
    }

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        resultDiv.className = "result success";
        resultDiv.textContent = data.message + " 로그인 페이지로 이동합니다...";
        resultDiv.style.display = "block";

        // 로그인 페이지로 이동
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else {
        resultDiv.className = "result error";
        resultDiv.textContent = data.detail || "회원가입에 실패했습니다.";
        resultDiv.style.display = "block";
      }
    } catch (error) {
      console.error("Error:", error);
      resultDiv.className = "result error";
      resultDiv.textContent = "서버 연결에 실패했습니다.";
      resultDiv.style.display = "block";
    }
  });
}
