import { useState, useEffect } from "react";
import ContactList from "./ContactList";
import "./App.css";
import ContactForm from "./ContactForm";

function App() {
  const [contacts, setContacts] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentContact, setCurrentContact] = useState({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);

  const fetchContacts = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setIsLoggedIn(false);
        return;
      }
      const response = await fetch("http://127.0.0.1:5000/contacts", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setContacts(data.contacts);
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
        localStorage.removeItem("token");
      }
    } catch (err) {
      setError("Failed to connect to the server");
      setIsLoggedIn(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setError("");
        setIsRegistering(false); // Switch to login form
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError("Failed to connect to the server");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("token", data.token);
        setIsLoggedIn(true);
        setError("");
        await fetchContacts();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError("Failed to connect to the server");
    }
  };

  const handleLogout = async () => {
    try {
      localStorage.removeItem("token");
      setIsLoggedIn(false);
      setContacts([]);
      setUsername("");
      setPassword("");
      setError("");
    } catch (err) {
      setError("Failed to logout");
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentContact({});
  };

  const openCreateModal = () => {
    if (!isModalOpen) setIsModalOpen(true);
  };

  const openEditModal = (contact) => {
    if (isModalOpen) return;
    setCurrentContact(contact);
    setIsModalOpen(true);
  };

  const onUpdate = () => {
    closeModal();
    fetchContacts();
  };

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        await fetchContacts();
      } catch (err) {
        setIsLoggedIn(false);
      }
    };
    checkLoginStatus();
  }, []);

  return (
    <div className="container mx-auto p-6 max-w-lg">
      {!isLoggedIn ? (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            {isRegistering ? "Register for Contact Manager" : "Contact Manager Login"}
          </h2>
          <form onSubmit={isRegistering ? handleRegister : handleLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 p-3 border border-gray-300 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter username"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 p-3 border border-gray-300 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter password"
              />
            </div>
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-md transition duration-200"
            >
              {isRegistering ? "Register" : "Login"}
            </button>
          </form>
          <button
            className="w-full mt-4 text-blue-600 hover:underline"
            onClick={() => setIsRegistering(!isRegistering)}
          >
            {isRegistering ? "Switch to Login" : "Switch to Register"}
          </button>
        </div>
      ) : (
        <>
          <button
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-md mb-6 transition duration-200"
            onClick={handleLogout}
          >
            Logout
          </button>
          <ContactList
            contacts={contacts}
            updateContact={openEditModal}
            updateCallback={onUpdate}
          />
          <button
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-md mt-4 transition duration-200"
            onClick={openCreateModal}
          >
            Create New Contact
          </button>
          {isModalOpen && (
            <div className="modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
              <div className="modal-content bg-white p-6 rounded shadow-lg max-w-md mx-auto">
                <span
                  className="close text-2xl cursor-pointer float-right"
                  onClick={closeModal}
                >
                  ×
                </span>
                <ContactForm
                  existingContact={currentContact}
                  updateCallback={onUpdate}
                />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;