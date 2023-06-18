import unittest
from gpt_engineer.chat_to_files import parse_chat

CODE_FORMATS = '''
(1)
File: main.py

```python
import pygame
````

(2)
entry.py
```python
import pygame
```

(3)
```python
# File: rickroll.py
import pygame
```

(4)
```python

# File: engineer.py
import pygame
```

(5)
```adastra.py
import pygame
```

(6)
```python bird.py
import pygame
```

(7)
```obstacle.py python
import pygame
```

(8)
```major1.py````
```python
import pygame
```

(9)
```major2.py````
```python
import pygame
```

(10)
```js
// File: bruh.js
const a = 1;
```

(11)
```swag.tsx
// File: swag.tsx
const a: number = 1;
```

(12)
```gmoita.ts
// File: gmoita.tsx
const a: number = 1;
```

(13)
** file1.py **
```python
import pygame
```

(14)
**file2.py**
```python
import pygame
```

(15)
#### `gm.py`
```python
import pygame
```
'''

class TestChatParsing(unittest.TestCase):
    
    def setUp(self):
        self._expected_filenames = (
            'main.py',
            'entry.py',
            'rickroll.py',
            'engineer.py',
            'adastra.py',
            'bird.py',
            'obstacle.py',
            'major1.py',
            'major2.py',
            'bruh.js',
            'swag.tsx',
            'gmoita.ts',
            'file1.py',
            'file2.py',
            'gm.py',
        )
        self.chat = CODE_FORMATS

    def test_parsing(self):
        codefiles = parse_chat(self.chat)

        self.assertEqual(len(codefiles), len(self._expected_filenames))
        for i, cf in enumerate(codefiles):
            filename, content = cf
            
            self.assertEqual(filename, self._expected_filenames[i])
            self.assertNotEqual(content, '')

if __name__ == '__main__':
    unittest.main()

