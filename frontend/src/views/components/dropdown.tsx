import React, {
  FunctionComponent,
  ReactNode,
  Children,
  cloneElement,
  useState,
  useRef,
  useEffect,
  Dispatch,
  SetStateAction,
} from "react";

interface Props {
  btnContent: ReactNode;
  dropdownClass?: string;
  btnClass?: string;
  useDropdown?: [boolean, Dispatch<SetStateAction<boolean>>],
}

const Dropdown: FunctionComponent<Props> = ({
  btnContent,
  dropdownClass,
  btnClass,
  children,
  useDropdown
}) => {

  let [active, setActive] = useState<boolean>(false)
  if (useDropdown) {
    // this is just to give the parent component an optional way
    // to access Dropdown component state (renderProps and similar is not optional)
    [active, setActive] = useDropdown;
  }
  const dropdownRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function handleEscape(evt: KeyboardEvent) {
      evt.stopPropagation();
      const esc_key_code = 27;
      if (evt.keyCode === esc_key_code) {
        hide();
      }
    }

    function handleDocumentClick(evt: MouseEvent) {
      evt.stopPropagation();
      const clicked = evt.target as any;
      // if the user click the dropdown or any of its children, do not hide the dropdown
      if (
        clicked === dropdownRef.current ||
        dropdownRef.current?.contains(clicked)
      ) {
        return;
      }
      // else hide it
      hide();
    }
    document.addEventListener("click", handleDocumentClick, false);
    document.addEventListener("keydown", handleEscape, false);

    // cleanup function
    return function () {
      document.removeEventListener("click", handleDocumentClick, false);
      document.removeEventListener("keydown", handleEscape, false);
    };
  }, []);

  function toggleMenu(evt: React.MouseEvent<HTMLButtonElement>) {
    if (active) {
      hide();
    } else {
      show();
    }
  }

  function hide() {
    setActive(false);
  }

  function show() {
    setActive(true);
  }

  return (
    <div ref={dropdownRef} className={dropdownClass ? dropdownClass + " dropdown" : "dropdown"}>
      <button
        className={btnClass ? btnClass + " btn" : "btn"}
        aria-haspopup="true"
        aria-expanded={active}
        onClick={toggleMenu}
      >
        {btnContent}
      </button>

      <div
        className={active ? "dropdown-menu show" : "dropdown-menu"}
        aria-labelledby="dropdownMenuLink"
      >
        {Children.map(children, (child: any) => {
          if (!child || !child.props) {
            return // not a react element
          }
          return cloneElement(child, {
            className: child.props.className
              ? child.props.className + " dropdown-item"
              : "dropdown-item",
          });
        })}
      </div>
    </div>
  );
};

export default Dropdown;
