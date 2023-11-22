import { createContext, Dispatch, SetStateAction } from 'react';

interface SidebarContextType {
  toggleSidebar: boolean;
  setToggleSidebar: Dispatch<SetStateAction<boolean>>;
  sidebarWidth?: number;
}

export const SidebarContext = createContext<Partial<SidebarContextType>>({});
