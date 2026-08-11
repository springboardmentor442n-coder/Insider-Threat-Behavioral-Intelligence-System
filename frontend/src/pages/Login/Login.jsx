import { useState } from "react";
import { FaShieldAlt, FaEye, FaEyeSlash } from "react-icons/fa";
import { loginUser } from "../../services/authService";
import "./Login.css";

export default function Login() {

    const [username, setUsername] = useState("");

    const [password, setPassword] = useState("");

    const [showPassword, setShowPassword] = useState(false);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");

    const handleLogin = async (e) => {

        e.preventDefault();

        setError("");

        setLoading(true);

        try {

            const data = await loginUser(username, password);

            localStorage.setItem(
                "access_token",
                data.access_token
            );

            window.location.href = "/dashboard";

        }

        catch (err) {

            console.error(err);

            setError("Invalid Username or Password");

        }

        finally {

            setLoading(false);

        }

    };

    return (

        <div className="login-container">

            <div className="login-card">

                <div className="logo-section">

                    <FaShieldAlt className="shield-icon"/>

                    <h1>Insider Threat</h1>

                    <p>Behavioral Intelligence System</p>

                </div>

                <form onSubmit={handleLogin}>

                    <div className="input-group">

                        <label>Username</label>

                        <input

                            type="text"

                            placeholder="Enter Username"

                            value={username}

                            onChange={(e)=>setUsername(e.target.value)}

                            required

                        />

                    </div>

                    <div className="input-group">

                        <label>Password</label>

                        <div className="password-box">

                            <input

                                type={showPassword ? "text":"password"}

                                placeholder="Enter Password"

                                value={password}

                                onChange={(e)=>setPassword(e.target.value)}

                                required

                            />

                            <button

                                type="button"

                                className="eye-btn"

                                onClick={()=>setShowPassword(!showPassword)}

                            >

                                {

                                    showPassword

                                    ?

                                    <FaEyeSlash/>

                                    :

                                    <FaEye/>

                                }

                            </button>

                        </div>

                    </div>

                    {

                        error &&

                        <div className="error-message">

                            {error}

                        </div>

                    }

                    <button

                        className="login-btn"

                        disabled={loading}

                    >

                        {

                            loading

                            ?

                            "Logging In..."

                            :

                            "Login"

                        }

                    </button>

                </form>

            </div>

        </div>

    );

}
