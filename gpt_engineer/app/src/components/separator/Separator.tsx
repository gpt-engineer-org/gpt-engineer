'use client';
import { Flex, useColorModeValue } from '@chakra-ui/react';

const HSeparator = (props: { variant?: string; [x: string]: any }) => {
  const textColor = useColorModeValue('gray.200', 'whiteAlpha.300');
  const { variant, ...rest } = props;
  return <Flex h="1px" w="100%" bg={textColor} {...rest} />;
};

const VSeparator = (props: { variant?: string; [x: string]: any }) => {
  const textColor = useColorModeValue('gray.200', 'whiteAlpha.300');
  const { variant, ...rest } = props;
  return <Flex w="1px" bg={textColor} {...rest} />;
};

export { HSeparator, VSeparator };
