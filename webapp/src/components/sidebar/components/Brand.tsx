'use client';
// Chakra imports
import {
  Img
} from '@chakra-ui/react';
import { Flex, useColorModeValue } from '@chakra-ui/react';
import logo from '../../../../public/img/layout/logo.png';
import { HSeparator } from '@/components/separator/Separator';

export function SidebarBrand() {
  //   Chakra color mode
  let logoColor = useColorModeValue('navy.700', 'white');

  return (
    <Flex alignItems="center" flexDirection="column">
      <Img src={logo.src} w="100px" h="100px" />
      <br />
    </Flex>
  );
}

export default SidebarBrand;
