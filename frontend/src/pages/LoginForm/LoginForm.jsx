import { useContext, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { UserContext } from '../../configs/context';
import Loading from '../../components/Loading/Loading';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate(); 
  const location = useLocation()
  const {from} = location['state'] || {from: "/home"}
  const {setUser} = useContext(UserContext)
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setIsLoading(true)
      const res = await axios.post('http://localhost:8000/api/login/', {
        username,
        password,
      });
      const accessToken = res['data']['access']
      if (accessToken) {
        localStorage.setItem('token', res.data.access);
        const fetchUser = await axios.get('http://localhost:8000/api/get_self/',{
          headers: {
            Authorization: "Bearer " + accessToken
          }
        })
        setUser(fetchUser['data'])
        navigate(from)
      }
    } catch (err) {
      setMessage("❌ Sai tài khoản hoặc mật khẩu.", err);
    }
    finally {
      setIsLoading(false)
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100" style={{ backgroundColor: "#fff5f5" }}>
      {isLoading && <Loading/>}
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
          <Link to='/register' className="text-muted" style={{ fontSize: "14px" }} >Don't have an account?</Link>
          {message && <div className="mt-2 text-danger">{message}</div>}
        </div>
      </div>
    </div>
  );
}

