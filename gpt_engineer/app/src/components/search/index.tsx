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
  children?: JSX.Element;
  borderRadius?: string;
  value?: string | number;
  [x: string]: any;
}) {
  // Pass the computed styles into the `__css` prop
  const { variant, children, borderRadius, ...rest } = props;
  // Chakra Color Mode
  const searchIconColor = useColorModeValue('gray.700', 'white');
  const searchColor = useColorModeValue('gray.700', 'white');
  const inputBg = useColorModeValue('transparent', 'navy.800');
  return (
    <InputGroup
      zIndex="0"
      bg={inputBg}
      border="1px solid"
      color={searchColor}
      borderColor={useColorModeValue('gray.200', 'whiteAlpha.100')}
      borderRadius="14px"
      _placeholder={{ color: 'gray.500' }}
      me={{ base: '10px', md: '20px' }}
      {...rest}
    >
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
            bg: 'none',
            transform: 'none',
            borderColor: 'transparent',
          }}
          _focus={{
            boxShadow: 'none',
          }}
          icon={<SearchIcon color={searchIconColor} w="15px" h="15px" />}
        />
      </InputLeftElement>
      <Input
        w={{
          base: '100px',
          md: '270px',
          lg: '530px',
          xl: '660px',
          '2xl': '860px',
          '3xl': '860px',
        }}
        maxW="100%"
        variant="search"
        fontSize="sm"
        bg={inputBg}
        color={searchColor}
        fontWeight="500"
        _placeholder={{ color: 'gray.500', fontSize: '14px' }}
        borderRadius={borderRadius ? borderRadius : '14px'}
        placeholder="Search..."
      />
    </InputGroup>
  );
}
