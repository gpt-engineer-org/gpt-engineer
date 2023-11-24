import ReactMarkdown from 'react-markdown'
import { useColorModeValue } from '@chakra-ui/react'
import Card from '@/components/card/Card'

export default function MessageBox(props: { output: string }) {
  const { output } = props
  const textColor = useColorModeValue('navy.700', 'white')
  return (
    <Card
      display={output ? 'flex' : 'none'}
      px="22px !important"
      pl="22px !important"
      color={textColor}
      minH="450px"
      fontSize={{ base: 'sm', md: 'md' }}
      lineHeight={{ base: '24px', md: '26px' }}
      fontWeight="500"
    >
      <ReactMarkdown className="font-medium">
        {output ? output : ''}
      </ReactMarkdown>
    </Card>
  )
}
