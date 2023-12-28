// eslint-disable-next-line no-unused-vars
import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Nav.css'

function Nav() {
  // Define navigation links in an array
  const navLinks = [
    { path: "/", title: "Home" },
    { path: "/committees", title: "Committees" },
    { path: "/bills", title: "Bills" },
    { path: "/members", title: "Members" }
  ];

  return (
    <nav className="nav-bar"> 
      <ul>
        {navLinks.map(link => ( // Dynamically create list items
          <li key={link.title}>
            <Link to={link.path}>{link.title}</Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Nav;
