# Pre-loaded Phong shaders

fragment = r"""# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
in vec3 position_view_space;   // the position in view coordinates of this fragment

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec3 final_color;

// === uniform here the texture object to sample from
uniform int mode;	// the rendering mode (better to code different shaders!)

// material uniforms
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

// light source
uniform vec3 light;
uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;

///=== main shader code
void main() {
      // 1. calculate vectors used for shading calculations
      vec3 camera_direction = -normalize(position_view_space);
      vec3 light_direction = normalize(light-position_view_space);

      // 2. Calculate the normal to the fragment using position of its neighbours
      vec3 xTangent = dFdx( position_view_space );
      vec3 yTangent = dFdy( position_view_space );
      vec3 normal_view_space = normalize( cross( xTangent, yTangent ) );

      // 3. now we calculate light components
      vec3 ambient = Ia*Ka;
      vec3 diffuse = Id*Kd*max(0.0f,dot(light_direction, normal_view_space));
      vec3 specular = Is*Ks*pow(max(0.0f, dot(reflect(light_direction, normal_view_space), -camera_direction)), Ns);

      // 4. we calculate the attenuation function
      // in this formula, dist should be the distance between the surface and the light
      float dist = length(light - position_view_space);
      float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

      // 5. Finally, we combine the shading components
      final_color = ambient + attenuation*(diffuse + specular);
}"""


vertex = r"""#version 130		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal
in vec3 color; 		// store the vertex colour
in vec2 texCoord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_color;        // the output of the shader will be the colour of the vertex
out vec3 position_view_space;   // the position of the vertex in view coordinates
out vec3 normal_view_space;     // the normal of the vertex in view coordinates
out vec2 fragment_texCoord;

//=== uniforms
uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform
uniform mat4 VM; 	// the View-Model matrix is received as a Uniform
uniform mat3 VMiT;  // The inverse-transpose of the view model matrix, used for normals
uniform int mode;	// the rendering mode (better to code different shaders!)


void main() {
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // those will be interpolate before being sent to the
    // fragment shader.
    // TODO WS4
    position_view_space = vec3(VM*vec4(position,1.0f));
    normal_view_space = normalize(VMiT*normal);

    // 3. forward the texture coordinates.
    fragment_texCoord = texCoord;

    // 4. for now, we just pass on the color from the data array
    fragment_color = color;
}"""