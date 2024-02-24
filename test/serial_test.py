import unittest
from dataclasses import dataclass
from enum import Enum
from typing import List

from tmt.serial import Serial


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


if __name__ == '__main__':
    unittest.main()
