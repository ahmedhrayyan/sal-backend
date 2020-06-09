import React from "react";
import logo from "../../logo.svg";
import alert from "../../images/icons/alert.svg";
import questionMark from "../../images/icons/question-mark.svg";
import Avatar from "./avatar";
import Dropdown from "./dropdown";
import { connect } from "react-redux";
import { Auth0Client } from "@auth0/auth0-spa-js";

interface NavProps {
  user: any,
  logout: () => void;
  goToProfile: () => void;
}
function Nav(props: NavProps) {
  return (
    <ul className="navbar-nav">
      <li className="nav-item">
        <button className="nav-btn btn">
          <img src={alert} alt="alert-icon" className="icon" />
        </button>
      </li>
      <li className="nav-item">
        <button className="nav-btn btn">
          <img src={questionMark} alt="question-mark-icon" className="icon" />
        </button>
      </li>
      <li className="nav-item">
        <Dropdown
          btnContent={<Avatar src={props.user.picture} size="sm" />}
          btnClass="avatar-btn"
        >
          <button onClick={props.goToProfile}>{props.user.name}</button>
          <button onClick={props.logout}>Logout</button>
        </Dropdown>
      </li>
    </ul>
  );
}

interface Props {
  auth0Client: Auth0Client;
  isAuthenticated: boolean;
  user: any
}
function Navbar(props: Props) {
  function login() {
    props.auth0Client.loginWithRedirect({});
  }

  function logout() {
    props.auth0Client.logout({returnTo: window.location.origin})
  }

  function goToProfile() {
    window.alert('Users profile page is not here yet, Stay tuned!')
  }

  return (
    <nav className="navbar navbar-primary navbar-dark">
      <a className="navbar-brand logo" href="#">
        <img
          className="logo-img"
          src={logo}
          width="30"
          height="30"
          alt="sal logo"
          loading="lazy"
        />
        <span className="logo-slogan">any question...</span>
      </a>
      <form className="form-inline navbar-search">
        <input
          className="form-control mr-sm-2"
          type="search"
          placeholder="Search"
          aria-label="Search"
        />
      </form>
      {!props.isAuthenticated && (
        <button className="btn btn-link-light" onClick={login}>
          Login
        </button>
      )}
      {props.isAuthenticated && (
        <Nav user={props.user} logout={logout} goToProfile={goToProfile} />
      )}
    </nav>
  );
}

function mapStateToProps(state: any) {
  return {
    auth0Client: state.auth0Client,
    isAuthenticated: state.isAuthenticated,
    user: state.user
  };
}

const mapDisptachToProps = {};

export default connect(mapStateToProps, mapDisptachToProps)(Navbar);
