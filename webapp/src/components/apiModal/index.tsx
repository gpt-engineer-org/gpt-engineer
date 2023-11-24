'use client';
import Card from '@/components/card/Card';
import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Box,
  Button,
  Flex,
  Icon,
  Input,
  Link,
  ListItem,
  UnorderedList,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Text,
  useColorModeValue,
  useDisclosure,
  useToast,
} from '@chakra-ui/react';
import { useState } from 'react';
import { MdLock } from 'react-icons/md';

function APIModal(props: { setApiKey: any; sidebar?: boolean }) {
  const { setApiKey, sidebar } = props;
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [inputCode, setInputCode] = useState<string>('');

  const textColor = useColorModeValue('navy.700', 'white');
  const grayColor = useColorModeValue('gray.500', 'gray.500');
  const inputBorder = useColorModeValue('gray.200', 'whiteAlpha.200');
  const inputColor = useColorModeValue('navy.700', 'white');
  const link = useColorModeValue('brand.500', 'white');
  const navbarIcon = useColorModeValue('gray.500', 'white');
  const toast = useToast();

  const handleChange = (Event: any) => {
    setInputCode(Event.target.value);
  };

  const handleApiKeyChange = (value: string) => {
    setApiKey(value);

    localStorage.setItem('apiKey', value);
  };
  return (
    <>
      {sidebar ? (
        <Button
          onClick={onOpen}
          display="flex"
          variant="api"
          fontSize={'sm'}
          fontWeight="600"
          borderRadius={'45px'}
          mt="8px"
          minH="40px"
        >
          Set API Key
        </Button>
      ) : (
        <Button
          onClick={onOpen}
          minW="max-content !important"
          p="0px"
          me="10px"
          _hover={{ bg: 'none' }}
          _focus={{ bg: 'none' }}
          _selected={{ bg: 'none' }}
          bg="none !important"
        >
          <Icon w="18px" h="18px" as={MdLock} color={navbarIcon} />
        </Button>
      )}

      <Modal blockScrollOnMount={false} isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent bg="none" boxShadow="none">
          <Card textAlign={'center'}>
            <ModalHeader
              fontSize="22px"
              fontWeight={'700'}
              mx="auto"
              textAlign={'center'}
              color={textColor}
            >
              Enter your OpenAI API Key
            </ModalHeader>
            <ModalCloseButton _focus={{ boxShadow: 'none' }} />
            <ModalBody p="0px">
              <Text
                color={grayColor}
                fontWeight="500"
                fontSize="md"
                lineHeight="28px"
                mb="22px"
              >
                You need an OpenAI API Key to use Horizon AI Template's
                features. Your API Key is stored locally on your browser and
                never sent anywhere else.
              </Text>
              <Flex mb="20px">
                <Input
                  h="100%"
                  border="1px solid"
                  borderColor={inputBorder}
                  borderRadius="45px"
                  p="15px 20px"
                  me="10px"
                  fontSize="sm"
                  fontWeight="500"
                  _focus={{ borderColor: 'none' }}
                  _placeholder={{ color: 'gray.500' }}
                  color={inputColor}
                  placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  onChange={handleChange}
                  value={inputCode}
                />
                <Button
                  variant="chakraLinear"
                  py="20px"
                  px="16px"
                  fontSize="sm"
                  borderRadius="45px"
                  ms="auto"
                  mb={{ base: '20px', md: '0px' }}
                  w={{ base: '300px', md: '180px' }}
                  h="54px"
                  onClick={() => {
                    inputCode?.includes('sk-')
                      ? handleApiKeyChange(inputCode)
                      : null;
                    if (inputCode)
                      toast({
                        title: inputCode?.includes('sk-')
                          ? `Success! You have successfully added your API key!`
                          : !inputCode?.includes('sk-')
                          ? `Invalid API key. Please make sure your API key is still working properly.`
                          : 'Please add your API key!',
                        position: 'top',
                        status: inputCode?.includes('sk-')
                          ? 'success'
                          : !inputCode?.includes('sk-')
                          ? `error`
                          : !inputCode
                          ? 'warning'
                          : 'error',
                        isClosable: true,
                      });
                  }}
                >
                  Save API Key
                </Button>
              </Flex>
              <Link
                color={link}
                fontSize="sm"
                href="https://platform.openai.com/account/api-keys"
                textDecoration="underline !important"
                fontWeight="600"
              >
                Get your API key from Open AI Dashboard
              </Link>
              <Accordion allowToggle w="100%" my="16px">
                <AccordionItem border="none">
                  <AccordionButton
                    borderBottom="0px solid"
                    maxW="max-content"
                    mx="auto"
                    _hover={{ border: '0px solid', bg: 'none' }}
                    _focus={{ border: '0px solid', bg: 'none' }}
                  >
                    <Box flex="1" textAlign="left">
                      <Text
                        color={textColor}
                        fontWeight="700"
                        fontSize={{ sm: 'md', lg: 'md' }}
                      >
                        Your API Key is not working?
                      </Text>
                    </Box>
                    <AccordionIcon color={textColor} />
                  </AccordionButton>
                  <AccordionPanel p="18px 0px 10px 0px">
                    <UnorderedList p="5px">
                      <ListItem
                        mb="26px"
                        color={grayColor}
                        fontSize=",d"
                        fontWeight="500"
                      >
                        Make sure you have an{' '}
                        <Link
                          textDecoration="underline"
                          fontSize=",d"
                          href="https://platform.openai.com/account/"
                          fontWeight="500"
                          color={grayColor}
                        >
                          OpenAI account
                        </Link>{' '}
                        and a valid API key to use ChatGPT. We don't sell API
                        keys.
                      </ListItem>
                      <ListItem
                        color={grayColor}
                        fontSize="md"
                        lineHeight="28px"
                        fontWeight="500"
                      >
                        Make sure you have your billing info added in{' '}
                        <Link
                          textDecoration="underline"
                          fontSize="md"
                          lineHeight="28px"
                          href="https://platform.openai.com/account/billing/overview"
                          fontWeight="500"
                          color={grayColor}
                        >
                          OpenAI Billing
                        </Link>{' '}
                        page. Without billing info, your API key will not work.
                      </ListItem>
                    </UnorderedList>
                  </AccordionPanel>
                </AccordionItem>
              </Accordion>
              <Text
                color={grayColor}
                fontWeight="500"
                fontSize="sm"
                mb="42px"
                mx="30px"
              >
                *The app will connect to OpenAI API server to check if your API
                Key is working properly.
              </Text>
            </ModalBody>
          </Card>
        </ModalContent>
      </Modal>
    </>
  );
}

export default APIModal;
