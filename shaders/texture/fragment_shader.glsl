# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
//in vec3 fragment_color;        // the fragment colour
//in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec2 fragment_texCoord;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;


// texture samplers
uniform sampler2D textureObject; // first texture object

///=== main shader code
void main() {
    // sample from the texture
    vec4 texval = vec4(1.0f);

    // sample from the texture
    texval = texture2D(textureObject, fragment_texCoord);

    // 5. Finally, we combine the shading components
    // we do not apply the texture to the specular component.
    final_color = texval;
}


