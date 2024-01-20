import { Link } from 'react-router-dom';
import styled from 'styled-components';

// Styled components
const NavBar = styled.nav`
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background-color: #4a90e2; // A vibrant blue
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: left;
  padding: 0.5rem 1rem;
  position: fixed;
  top: 0;
  width: 100%;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
`;

const StyledLink = styled(Link)`
  color: white;
  text-decoration: none;
  &:hover {
    color: #eed85b; // Gold color for hover
  }
`;

const NavList = styled.ul`
  list-style-type: none;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: center;
`;

const NavItem = styled.li`
  margin: 0 15px;
`;

// React component
function Nav() {
  const navLinks = [
    { path: "/", title: "Home" },
    { path: "/committees", title: "Committees" },
    { path: "/bills", title: "Bills" },
    { path: "/members", title: "Members" }
  ];

  return (
    <NavBar>
      <NavList>
        {navLinks.map(link => (
          <NavItem key={link.title}>
            <StyledLink to={link.path}>{link.title}</StyledLink>
          </NavItem>
        ))}
      </NavList>
    </NavBar>
  );
}

export default Nav;
