import { useContext, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Loading from '../../components/Loading/Loading';


export default function RegisterForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [repassword, setRePassword] = useState('');
  const [message, setMessage] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const navigator = useNavigate()
  const handleRegister = async (e) => {
    e.preventDefault();
    if (repassword !== password) {
      setMessage('Password does not match!')
    }
    try {
      setIsLoading(true)
      const res = await axios.post('http://localhost:8000/api/register/', {
        username,
        password,
      });
      if (res['status'] === 201) {
        navigator('/login')
      }
    } catch (err) {
      setMessage("❌ Tạo tài khoản không thành công", err);
    }
    finally {
      setIsLoading(false)
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100" style={{ backgroundColor: "#fff5f5" }}>
      {isLoading && <Loading/>}
      <div className="p-4 bg-white rounded-4 shadow" style={{ width: "400px" }}>
        <h2 className="text-center fw-bold mb-1">Sign Up</h2>
        <p className="text-center text-muted mb-4">Enter the information below</p>
        <form onSubmit={handleRegister}>
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
          <div className="mb-3">
            <input
              type="password"
              className="form-control"
              placeholder="Confirm your password"
              value={repassword}
              onChange={(e) => setRePassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-danger w-100 fw-bold">
            Sign up
          </button>
        </form>
        <div className="text-center mt-3">
          {message && <div className="mt-2 text-danger">{message}</div>}
        </div>
      </div>
    </div>
  );
}

