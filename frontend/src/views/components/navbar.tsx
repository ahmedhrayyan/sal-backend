import React, { useState, FormEvent } from "react";
import logo from "../../images/logo.svg";
import alert from "../../images/icons/alert.svg";
import questionMark from "../../images/icons/question-mark.svg";
import Avatar from "./avatar";
import Dropdown from "./dropdown";
import { connect } from "react-redux";
import { Auth0Client } from "@auth0/auth0-spa-js";
import { User } from "../../state/ducks/users/types";
import { Link, useHistory } from "react-router-dom";

interface NavProps {
  user: User | null;
  logout: () => void;
  goToProfile: () => void;
}
function Nav(props: NavProps) {
  function handleAlertClick() {
    window.alert("Alerts not implemented yet, Stay tuned!");
  }
  let currentUser,
    userName = "loading...";
  if (props.user) {
    currentUser = props.user;
    userName = currentUser.user_metadata
      ? currentUser.user_metadata.firstname +
        " " +
        currentUser.user_metadata.lastname
      : currentUser.name;
  }
  return (
    <ul className="navbar-nav">
      <li className="nav-item">
        <button className="nav-btn btn" onClick={handleAlertClick}>
          <img src={alert} alt="alert-icon" className="icon" />
        </button>
      </li>
      <li className="nav-item">
        <button className="nav-btn btn">
          <img src={questionMark} alt="question-mark-icon" className="icon" />
        </button>
      </li>
      <li className="nav-item" style={{ marginRight: "-7px" }}>
        <Dropdown
          btnContent={<Avatar src={currentUser?.picture || ""} size="sm" />}
          btnClass="avatar-btn"
        >
          <button
            onClick={props.goToProfile}
            style={{ textTransform: "capitalize" }}
          >
            {userName}
          </button>
          <button onClick={props.logout}>Logout</button>
        </Dropdown>
      </li>
    </ul>
  );
}

interface Props {
  auth0: Auth0Client;
  isAuthenticated: boolean;
  currentUser: string;
  isFetching: boolean;
  users: Map<string, User>;
}
function Navbar(props: Props) {
  const history = useHistory();
  const [inputVal, setInputVal] = useState<string>("");
  function login() {
    props.auth0.loginWithRedirect({});
  }

  function logout() {
    props.auth0.logout({ returnTo: window.location.origin });
  }

  function goToProfile() {
    window.alert("Users profile page is not here yet, Stay tuned!");
  }

  function handleSearch(evt: any) {
    evt.preventDefault();
    if (!inputVal) {
      return null;
    }
    history.push(`/search?term=${inputVal}`);
  }

  function handleChange(evt: FormEvent<HTMLInputElement>) {
    setInputVal(evt.currentTarget.value);
  }

  return (
    <nav className="navbar navbar-primary navbar-dark">
      <Link to="/" className="navbar-brand logo">
        <img
          className="logo-img"
          src={logo}
          width="30"
          height="30"
          alt="sal logo"
          loading="lazy"
        />
        <span className="logo-slogan">any question...</span>
      </Link>
      <form className="form-inline navbar-search" onSubmit={handleSearch}>
        <input
          className="form-control mr-sm-2"
          type="search"
          placeholder="Search"
          aria-label="Search"
          value={inputVal}
          onChange={handleChange}
        />
      </form>
      {!props.isAuthenticated && (
        <button
          className="btn btn-link-light"
          onClick={login}
          style={{
            paddingRight: "10px",
            paddingLeft: "10px",
            marginRight: "-10px",
          }}
        >
          Sign In
        </button>
      )}
      {props.isAuthenticated && (
        <Nav
          user={props.users.get(props.currentUser) || null}
          logout={logout}
          goToProfile={goToProfile}
        />
      )}
    </nav>
  );
}

function mapStateToProps(state: any) {
  return {
    auth0: state.auth0.client,
    isAuthenticated: state.auth0.isAuthenticated,
    currentUser: state.auth0.currentUser,
    isFetching: state.users.isFetching,
    users: state.users.entities,
  };
}

const mapDispatchToProps = {};

export default connect(mapStateToProps, mapDispatchToProps)(Navbar);
