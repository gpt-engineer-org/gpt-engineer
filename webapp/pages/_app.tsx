import React, { useEffect, useState } from "react";
import { AppProps } from "next/app";
import { ChakraProvider, Box, Portal, useDisclosure } from "@chakra-ui/react";
import theme from "@/theme/theme";
import routes from "@/routes";
import Sidebar from "@/components/sidebar/Sidebar";
import Footer from "@/components/footer/FooterAdmin";
import Navbar from "@/components/navbar/NavbarAdmin";
import { getActiveRoute, getActiveNavbar } from "@/utils/navigation";
import { usePathname } from "next/navigation";
import "@/styles/App.css";
import "@/styles/Contact.css";
import "@/styles/Plugins.css";
import "@/styles/MiniCalendar.css";
import { socket } from "@/socket";
import { ConnectionState } from "@/components/ConnectionState";
import { ConnectionManager } from "@/components/ConnectionManager";
import { Events } from "@/components/Events";

interface GPTEventProps {
  events: string[];
}

function App({ Component, pageProps }: AppProps<{}>) {
  const pathname = usePathname();
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [GPTEvents, setGPTEvents] = useState<string[]>([]);
  const [apiKey, setApiKey] = useState("");
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    const initialKey = localStorage.getItem("apiKey");
    if (initialKey?.includes("sk-") && apiKey !== initialKey) {
      setApiKey(initialKey);
    }

    socket.connect();

    function onConnect() {
      console.log("Socket.IO is connected");
      setIsConnected(true);
    }

    function onDisconnect() {
      console.log("Socket.IO is disconnected");
      setIsConnected(false);
    }

    function onGPTEvent(value: string) {
      console.log(`GPT event ${value}`);
      setGPTEvents((previous) => [...previous, value]);
    }

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("event", onGPTEvent);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
      socket.off("event", onGPTEvent);
    };
  }, [apiKey]);

  return (
    <>
      <ConnectionState isConnected={isConnected} />
      <Events events={GPTEvents} />
      <ConnectionManager />
      <ChakraProvider theme={theme}>
        <Box>
          <Sidebar setApiKey={setApiKey} routes={routes} />
          <Box
            pt={{ base: "60px", md: "100px" }}
            float="right"
            minHeight="100vh"
            height="100%"
            overflow="auto"
            position="relative"
            maxHeight="100%"
            w={{ base: "100%", xl: "calc( 100% - 290px )" }}
            maxWidth={{ base: "100%", xl: "calc( 100% - 290px )" }}
            transition="all 0.33s cubic-bezier(0.685, 0.0473, 0.346, 1)"
            transitionDuration=".2s, .2s, .35s"
            transitionProperty="top, bottom, width"
            transitionTimingFunction="linear, linear, ease"
          >
            <Portal>
              <Box>
                <Navbar
                  setApiKey={setApiKey}
                  onOpen={onOpen}
                  logoText={"GPT-Engineer"}
                  brandText={getActiveRoute(routes, pathname)}
                  secondary={getActiveNavbar(routes, pathname)}
                />
              </Box>
            </Portal>
            <Box
              mx="auto"
              p={{ base: "20px", md: "30px" }}
              pe="20px"
              minH="100vh"
              pt="50px"
            >
              <Component apiKeyApp={apiKey} {...pageProps} />
            </Box>
            <Box>
              <Footer />
            </Box>
          </Box>
        </Box>
      </ChakraProvider>
    </>
  );
}

export default App;
