'use client';
/* eslint-disable */

// chakra imports
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Badge,
  Box,
  Flex,
  HStack,
  Text,
  List,
  Icon,
  ListItem,
  useColorModeValue,
  Link,
} from '@chakra-ui/react';
import { FaCircle } from 'react-icons/fa';
import { IoMdAdd } from 'react-icons/io';
import NavLink from '@/components/link/NavLink';
import { IRoute } from '@/types/navigation';
import { PropsWithChildren, useCallback } from 'react';
import { usePathname } from 'next/navigation';

interface SidebarLinksProps extends PropsWithChildren {
  routes: IRoute[];
}

export function SidebarLinks(props: SidebarLinksProps) {
  //   Chakra color mode
  const pathname = usePathname();
  let activeColor = useColorModeValue('navy.700', 'white');
  let inactiveColor = useColorModeValue('gray.500', 'gray.500');
  let borderColor = useColorModeValue('gray.200', 'whiteAlpha.300');
  let activeIcon = useColorModeValue('brand.500', 'white');
  let iconColor = useColorModeValue('navy.700', 'white');
  let gray = useColorModeValue('gray.500', 'gray.500');

  const { routes } = props;

  // verifies if routeName is the one active (in browser input)
  const activeRoute = useCallback(
    (routeName: string) => {
      return pathname?.includes(routeName);
    },
    [pathname],
  );

  // this function creates the links and collapses that appear in the sidebar (left menu)
  const createLinks = (routes: IRoute[]) => {
    return routes.map((route, key) => {
      if (route.collapse && !route.invisible) {
        return (
          <Accordion defaultIndex={0} allowToggle key={key}>
            <Flex w="100%" justifyContent={'space-between'}>
              <AccordionItem isDisabled border="none" mb="14px" key={key}>
                <AccordionButton
                  display="flex"
                  alignItems="center"
                  mb="4px"
                  justifyContent="center"
                  _hover={{
                    bg: 'unset',
                  }}
                  _focus={{
                    boxShadow: 'none',
                  }}
                  borderRadius="8px"
                  w="100%"
                  py="0px"
                  ms={0}
                >
                  {route.icon ? (
                    <Flex
                      align="center"
                      justifyContent="space-between"
                      w="100%"
                    >
                      <HStack
                        spacing={
                          activeRoute(route.path.toLowerCase())
                            ? '22px'
                            : '26px'
                        }
                      >
                        <Flex
                          w="100%"
                          alignItems="center"
                          justifyContent="center"
                        >
                          <Box
                            color={
                              route.disabled
                                ? gray
                                : activeRoute(route.path.toLowerCase())
                                ? activeIcon
                                : inactiveColor
                            }
                            me="12px"
                            mt="6px"
                          >
                            {route.icon}
                          </Box>
                          <Text
                            cursor="not-allowed"
                            me="auto"
                            color={
                              route.disabled
                                ? gray
                                : activeRoute(route.path.toLowerCase())
                                ? activeColor
                                : 'gray.500'
                            }
                            fontWeight="500"
                            letterSpacing="0px"
                            fontSize="sm"
                          >
                            {route.name}
                          </Text>
                        </Flex>
                      </HStack>
                    </Flex>
                  ) : (
                    <Flex pt="0px" pb="10px" alignItems="center" w="100%">
                      <HStack
                        spacing={
                          activeRoute(route.path.toLowerCase())
                            ? '22px'
                            : '26px'
                        }
                        ps="32px"
                      >
                        <Text
                          cursor="not-allowed"
                          me="auto"
                          fontWeight="500"
                          letterSpacing="0px"
                          fontSize="sm"
                        >
                          {route.name}
                        </Text>
                      </HStack>
                      <AccordionIcon
                        ms="auto"
                        color={route.disabled ? gray : 'gray.500'}
                      />
                    </Flex>
                  )}
                </AccordionButton>
                <AccordionPanel py="0px" ps={'8px'}>
                  <List>
                    {
                      route.icon && route.items
                        ? createLinks(route.items) // for bullet accordion links
                        : route.items
                        ? createAccordionLinks(route.items)
                        : '' // for non-bullet accordion links
                    }
                  </List>
                </AccordionPanel>
              </AccordionItem>
                <Badge
                  display={{ base: 'flex', lg: 'none', xl: 'flex' }}
                  colorScheme="brand"
                  borderRadius="25px"
                  color="brand.500"
                  textTransform={'none'}
                  letterSpacing="0px"
                  px="8px"
                >
                  Dir
                </Badge>
            </Flex>
          </Accordion>
        );
      } else if (!route.invisible) {
        return (
          <>
            {route.icon ? (
              <Flex
                align="center"
                justifyContent="space-between"
                w="100%"
                maxW="100%"
                ps="17px"
                mb="0px"
              >
                <HStack
                  w="100%"
                  mb="14px"
                  spacing={
                    activeRoute(route.path.toLowerCase()) ? '22px' : '26px'
                  }
                >
                  {route.name === 'Chat UI' ? (
                    <NavLink
                      href={
                        route.layout ? route.layout + route.path : route.path
                      }
                      key={key}
                      styles={{ width: '100%' }}
                    >
                      <Flex
                        w="100%"
                        alignItems="center"
                        justifyContent="center"
                      >
                        <Box
                          color={
                            route.disabled
                              ? gray
                              : activeRoute(route.path.toLowerCase())
                              ? activeIcon
                              : inactiveColor
                          }
                          me="12px"
                          mt="6px"
                        >
                          {route.icon}
                        </Box>
                        <Text
                          me="auto"
                          color={
                            route.disabled
                              ? gray
                              : activeRoute(route.path.toLowerCase())
                              ? activeColor
                              : 'gray.500'
                          }
                          fontWeight="500"
                          letterSpacing="0px"
                          fontSize="sm"
                        >
                          {route.name}
                        </Text>
                      </Flex>
                    </NavLink>
                  ) : (
                    <Flex
                      w="100%"
                      alignItems="center"
                      justifyContent="center"
                      cursor="not-allowed"
                    >
                      <Box
                        opacity="0.4"
                        color={
                          route.disabled
                            ? gray
                            : activeRoute(route.path.toLowerCase())
                            ? activeIcon
                            : inactiveColor
                        }
                        me="12px"
                        mt="6px"
                      >
                        {route.icon}
                      </Box>
                      <Text
                        opacity="0.4"
                        me="auto"
                        color={
                          route.disabled
                            ? gray
                            : activeRoute(route.path.toLowerCase())
                            ? activeColor
                            : 'gray.500'
                        }
                        fontWeight="500"
                        letterSpacing="0px"
                        fontSize="sm"
                      >
                        {route.name}
                      </Text>
                        <Badge
                          display={{ base: 'flex', lg: 'none', xl: 'flex' }}
                          colorScheme="brand"
                          borderRadius="25px"
                          color="brand.500"
                          textTransform={'none'}
                          letterSpacing="0px"
                          px="8px"
                        >
                          Dir
                        </Badge>
                    </Flex>
                  )}
                </HStack>
              </Flex>
            ) : (
              <ListItem ms={0} cursor="not-allowed" opacity={'0.4'}>
                <Flex ps="32px" alignItems="center" mb="8px">
                  <Text
                    color={
                      route.disabled
                        ? gray
                        : activeRoute(route.path.toLowerCase())
                        ? activeColor
                        : inactiveColor
                    }
                    fontWeight="500"
                    fontSize="xs"
                  >
                    {route.name}
                  </Text>
                </Flex>
              </ListItem>
            )}
          </>
        );
      }
    });
  };
  // this function creates the links from the secondary accordions (for example auth -> sign-in -> default)
  const createAccordionLinks = (routes: IRoute[]) => {
    return routes.map((route: IRoute, key: number) => {
      return (
        <ListItem
          ms="28px"
          display="flex"
          alignItems="center"
          mb="10px"
          key={key}
          cursor="not-allowed"
        >
          <Icon
            w="6px"
            h="6px"
            me="8px"
            as={FaCircle}
            color={route.disabled ? gray : activeIcon}
          />
          <Text
            color={
              route.disabled
                ? gray
                : activeRoute(route.path.toLowerCase())
                ? activeColor
                : inactiveColor
            }
            fontWeight={
              activeRoute(route.path.toLowerCase()) ? 'bold' : 'normal'
            }
            fontSize="sm"
          >
            {route.name}
          </Text>
        </ListItem>
      );
    });
  };
  //  BRAND
  return <>{createLinks(routes)}</>;
}

export default SidebarLinks;
