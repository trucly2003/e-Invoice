import { useState } from 'react';
import axios from 'axios';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [message, setMessage] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/api/login/', {
        username,
        password,
      });
      localStorage.setItem('token', res.data.access);
      setMessage("✅ Login thành công!");
    } catch (err) {
      setMessage("❌ Sai tài khoản hoặc mật khẩu.", err);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100" style={{ backgroundColor: "#fff5f5" }}>
      <div className="p-4 bg-white rounded-4 shadow" style={{ width: "400px" }}>
        <h2 className="text-center fw-bold mb-1">Sign In</h2>
        <p className="text-center text-muted mb-4">Enter the information below</p>
        <form onSubmit={handleLogin}>
          <div className="mb-3">
            <input
              type="text"
              className="form-control"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="mb-3">
            <input
              type="password"
              className="form-control"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="form-check mb-3">
            <input
              type="checkbox"
              className="form-check-input"
              id="remember"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
            />
            <label className="form-check-label" htmlFor="remember">
              Remember password
            </label>
          </div>
          <button type="submit" className="btn btn-danger w-100 fw-bold">
            Sign in
          </button>
        </form>
        <div className="text-center mt-3">
          <p className="text-muted mb-1" style={{ fontSize: "14px" }}>Forgot password?</p>
          <p className="text-muted" style={{ fontSize: "14px" }}>Don't have an account?</p>
          {message && <div className="mt-2 text-danger">{message}</div>}
        </div>
      </div>
    </div>
  );
}
