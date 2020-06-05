import React, { FunctionComponent } from 'react';
import logo from '../../logo.svg';
import alert from '../../images/icons/alert.svg';
import questionMark from '../../images/icons/question-mark.svg';
import dummyAvatar from "../../images/avatar.jpg";
import Avatar from './avatar';
import Dropdown from "./dropdown";

interface Props {

}

const Navbar: FunctionComponent<Props> = () => {

  return (
    <nav className="navbar navbar-primary navbar-dark">
      <a className="navbar-brand logo" href="#">
        <img className='logo-img' src={logo} width="30" height="30" alt="sal logo" loading="lazy" />
        <span className='logo-slogan'>any question...</span>
      </a>
      <form className="form-inline navbar-search">
        <input className="form-control mr-sm-2" type="search" placeholder="Search" aria-label="Search" />
      </form>
      <ul className="navbar-nav">
      <li className="nav-item">
        <button className="nav-btn btn">
          <img src={alert} alt="alert-icon" className="icon"/>
        </button>
      </li>
      <li className="nav-item">
        <button className="nav-btn btn">
          <img src={questionMark} alt="question-mark-icon" className="icon"/>
        </button>
      </li>
      <li className="nav-item">
        <Dropdown
          btnContent={<Avatar src={dummyAvatar} size="sm" />}
          btnClass='avatar-btn'
        >
          <a href="#">item1</a>
        </Dropdown>
      </li>
    </ul>
  </nav>
  )
}

export default Navbar
