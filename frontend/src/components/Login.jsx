import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';
import logo from '../assets/logo.png';

const Login = ({ setLoggedIn }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/api/login/`, {
        email,
        password,
      });
      if (response.data.success) {
        localStorage.setItem("access_token", response.data.access_token);
        setLoggedIn(true);
      } else {
        setErrorMsg(response.data.message || 'Login failed. Please try again.');
      }
    } catch (error) {
      if (error.response) {
        setErrorMsg(error.response.data.message || 'Login failed. Server error.');
      } else if (error.request) {
        setErrorMsg('Network error. Please check your connection.');
      } else {
        setErrorMsg('Login failed. Please try again.');
      }
    }
  };

  return (
    <div className="login-container">
      <div className="login-brand">
        <img src={logo} alt="OptiTraffic AI Logo" className="login-logo" />
        <h1>OptiTraffic AI</h1>
      </div>
      <form className="login-box" onSubmit={handleLogin}>
        <h2>Login</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {errorMsg && <p className="error">{errorMsg}</p>}
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
