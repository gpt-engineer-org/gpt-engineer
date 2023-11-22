'use client';
import {
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  useColorModeValue,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
export function SearchBar(props: {
  variant?: string;
  background?: string;
  children?: JSX.Element;
  placeholder?: string;
  borderRadius?: string | number;
  [x: string]: any;
}) {
  // Pass the computed styles into the `__css` prop
  const { variant, background, children, placeholder, borderRadius, ...rest } =
    props;
  // Chakra Color Mode
  const searchIconColor = useColorModeValue('gray.700', 'white');
  const inputBg = useColorModeValue('secondaryGray.300', 'navy.900');
  const inputText = useColorModeValue('gray.700', 'gray.100');
  return (
    <InputGroup w={{ base: '100%', md: '200px' }} {...rest}>
      <InputLeftElement>
        <IconButton
          aria-label="search"
          bg="inherit"
          borderRadius="inherit"
          _active={{
            bg: 'inherit',
            transform: 'none',
            borderColor: 'transparent',
          }}
          _hover={{
            bg: 'inherit',
            transform: 'none',
            borderColor: 'transparent',
          }}
          _focus={{
            boxShadow: 'none',
          }}
          icon={<SearchIcon color={searchIconColor} w="14px" h="14px" />}
        />
      </InputLeftElement>

      <Input
        variant="search"
        fontSize="sm"
        bg={background ? background : inputBg}
        color={inputText}
        fontWeight="500"
        _placeholder={{ color: 'gray.500', fontSize: '14px' }}
        borderRadius={borderRadius ? borderRadius : '30px'}
        placeholder={placeholder ? placeholder : 'Search'}
      />
    </InputGroup>
  );
}
