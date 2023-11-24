'use client';
// Chakra imports
import {
  Flex,
  FormLabel,
  Input,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';

export default function Default(props: {
  id?: string;
  label?: string;
  extra?: JSX.Element;
  placeholder?: string;
  type?: string;
  [x: string]: any;
}) {
  const { id, label, extra, placeholder, type, mb, ...rest } = props;
  // Chakra Color Mode
  const textColorPrimary = useColorModeValue('navy.700', 'white');
  const searchColor = useColorModeValue('gray.700', 'white');
  const inputBg = useColorModeValue('transparent', 'navy.800');
  const placeholderColor = useColorModeValue(
    { color: 'gray.500' },
    { color: 'whiteAlpha.600' },
  );

  return (
    <Flex direction="column" mb={mb ? mb : '30px'}>
      <FormLabel
        display="flex"
        ms="10px"
        htmlFor={id}
        fontSize="sm"
        color={textColorPrimary}
        fontWeight="bold"
        _hover={{ cursor: 'pointer' }}
      >
        {label}
        <Text fontSize="sm" fontWeight="400" ms="2px">
          {extra}
        </Text>
      </FormLabel>
      <Input
        {...rest}
        type={type}
        id={id}
        fontWeight="500"
        bg={inputBg}
        variant="main"
        fontSize="sm"
        placeholder={placeholder}
        _placeholder={placeholderColor}
        border="1px solid"
        color={searchColor}
        borderColor={useColorModeValue('gray.200', 'whiteAlpha.100')}
        borderRadius="12px"
        h="44px"
        maxH="44px"
      />
    </Flex>
  );
}
