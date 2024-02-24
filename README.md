# Serial-Py

这是一个基于`python typing`的反序列化框架，它已经发布到Pypi，因此，你可以通过如下方式依赖它：
```shell
pip3 install 
```

## 数据类定义
使用时需要将数据按照如下方式定义：这里面包含嵌套类、枚举类
等，如果需要序列化的字段名称和变量名称不完全一致，可以实现`Serial.name_strategy`实现字段名称之间的映射。

```python
from dataclasses import dataclass
from enum import Enum
from typing import List

from src.serial import Serial


class ShaderType(Enum):
    vertex = 1
    fragment = 2


@dataclass
class Shader(Serial):
    code: str = None
    shader: ShaderType = None
    attributes: List[int] = None
    compiled: bool = False
    attached: bool = False


@dataclass
class Program(Serial):
    vertex_shader: Shader = None
    fragment_shader: Shader = None
    linked: bool = False
    byte_buffers: List[float] = None
```

## 序列化
你可以调用`Serial.json()`将`class`转为`dict`，也可以调用`Serial.str()`直接将`class`转换为
字符串。
```python
class SerialTestCase(unittest.TestCase):
    vertex_shader = Shader(
        code="vertex shader",
        shader=ShaderType.vertex,
        attributes=[1, 2, 3],
        compiled=True,
        attached=False
    )
    fragment_shader = Shader(
        code="fragment shader",
        shader=ShaderType.fragment,
        attributes=[],
        compiled=False,
        attached=True
    )
    program = Program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader,
        linked=True,
        byte_buffers=[0.1, 0.2, 0.3]
    )

    def test_serialize(self):
        program_dict = self.program.json()
        print(program_dict)
        vertex_shader: dict = program_dict.get('vertex_shader')
        self.assertIsInstance(vertex_shader, dict)
        self.assertEqual(vertex_shader.get("compiled"), True)
        attributes = vertex_shader.get("attributes")
        self.assertIsInstance(attributes, list)
        self.assertEqual(len(attributes), 3)
        self.assertEqual(attributes[0], 1)
        program_str = self.program.str(indent=2, ensure_ascii=True)
        print(program_str)
```

## 反序列化
你可以直接调用如`Program.from_str(...)`或`Program.from_json(dict)`来将字符串或者字典转换成某种类型，
当然枚举类和嵌套类都是支持的，同样可以通过定义`Serial.name_strategy`来实现字段名称之间的映射。

```python
def test_de_serialize(self):
    json_str = """
    {
      "vertex_shader": {
        "shader": "vertex",
        "attributes": [
          1,
          2,
          3
        ],
        "compiled": true,
        "attached": false
      },
      "fragment_shader": {
        "shader": "fragment",
        "attributes": [],
        "compiled": false,
        "attached": true
      },
      "linked": true,
      "byte_buffers": [
        0.1,
        0.2,
        0.3
      ]
    }
    """.strip()

    de_serial_result = Program.from_str(json_str)
    self.assertIsInstance(de_serial_result, Program)
    self.assertTrue(de_serial_result.linked)
    buffers = de_serial_result.byte_buffers
    self.assertIsInstance(buffers, list)
    self.assertEqual(len(buffers), 3)

    # for nested classes
    vertex_shader = de_serial_result.vertex_shader
    self.assertIsInstance(vertex_shader, Shader)
    self.assertTrue(vertex_shader.compiled)
    self.assertFalse(vertex_shader.attached)
    self.assertIsInstance(vertex_shader.attributes, list)
    self.assertEqual(vertex_shader.attributes.__len__(), 3)
    # for enum
    self.assertIsInstance(vertex_shader.shader, ShaderType)
    self.assertEqual(vertex_shader.shader, ShaderType.vertex)

    fragment_shader = de_serial_result.fragment_shader
    self.assertIsInstance(fragment_shader, Shader)
    self.assertTrue(fragment_shader.attached)
    self.assertIsInstance(fragment_shader.attributes, list)
    self.assertEqual(len(fragment_shader.attributes), 0)
```