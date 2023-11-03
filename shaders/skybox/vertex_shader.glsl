#version 130

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
//in vec3 vertex_position;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_texCoord;

uniform mat4 PVM;

void main(void)
{
	gl_Position = PVM*vec4(position, 1);
	gl_Position.z = gl_Position.w*0.9999;
	fragment_texCoord = -position;
}
