# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec3 normal_view_space;     // the normal in view coordinates to this fragment
in vec2 fragment_texCoord;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;

//=== uniforms
uniform int mode;	// the rendering mode (better to code different shaders!)
uniform int has_texture;
uniform sampler2D textureObject; // texture object
uniform sampler2DShadow shadow_map;
//uniform sampler2D old_map;

// shadow map matrix
// this shadow map matrix times the fragment shader position allows looking up the depth in the shadow map texture
uniform mat4 shadow_map_matrix;

// material uniforms
uniform vec3 Ka;    // ambient reflection properties of the material
uniform vec3 Kd;    // diffuse reflection propoerties of the material
uniform vec3 Ks;    // specular properties of the material
uniform float Ns;   // specular exponent

// light source
uniform vec3 light; // light position in view space
uniform vec3 Ia;    // ambient light properties
uniform vec3 Id;    // diffuse properties of the light source
uniform vec3 Is;    // specular properties of the light source

uniform float alpha = 1.0f;


vec4 phong(vec4 texval);

vec4 phong(vec4 texval) {
        // 1. calculate vectors used for shading calculations
    // TODO WS4
    vec3 camera_direction = -normalize(position_view_space);
    vec3 light_direction = normalize(light-position_view_space);

    // 2. now we calculate light components
    // TODO WS4
    vec4 ambient = vec4(Ia*Ka,alpha);
    vec4 diffuse = vec4(Id*Kd*max(0.0f,dot(light_direction, normal_view_space)), alpha);
    vec4 specular = vec4(Is*Ks*pow(max(0.0f, dot(reflect(light_direction, normal_view_space), -camera_direction)), Ns), alpha);

    // 3. we calculate the attenuation function
    // in this formula, dist should be the distance between the surface and the light
    float dist = length(light - position_view_space);
    float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

    // 5. Finally, we combine the shading components
    return texval*ambient + attenuation*(texval*diffuse + specular);
}

///=== main shader code
void main() {

    // 4. we sample from the texture map
    // the texture2D function just samples from the texture object at coordinates set by fragment_texCoord
    // using interpolation/extrapolation as set in the OpenGL program
    vec4 texval = vec4(1.0f);
    if(has_texture == 1)
        texval = texture2D(textureObject, fragment_texCoord);

    final_color = vec4(0.0f);

    // 5. Finally, we combine the shading components

    final_color = phong(texval);

    vec4 p = shadow_map_matrix*vec4(position_view_space, 1);

    //float zlight = texture(old_map, p.xy/p.w).r;

    //if( zlight > -p.z/p.w )
     //  final_color=vec4(0,0,0,0);

    //final_color = vec4( 0, p.z/p.w/10, 0, 1.0f );

    /*
    if(p.z/p.w < 0)
        final_color.x = 1.0;
    else
        if(p.z/p.w > 1)
            final_color.z = 1.0;
        else
            final_color.y = p.z/p.w;

    if(zlight < 1.01*p.z/p.w)
        final_color = vec4(0);
*/

	if (p.w > 0)
	{
		p.xyz /= p.w;

		//p.xyz = -p.xyz*0.5 + 0.5;

		p.z *= 0.999;

		// this is another alternative that also works:
		//p.z -= 0.01;

		float val = texture(shadow_map, p.xyz);
        //if (val < 0.5f)
		//	final_color.xyz = Ka*Ia*texval.xyz; //
        final_color.xyz = (1.0-val)*Ka*Ia*texval.xyz + val*final_color.xyz;

        //if (p.z > 0.9)
         //   final_color.xyz = Ka*Ia*texval.xyz;

        //final_color = vec4(p.z, 0.0f, 0.0f, 1.0f);
        //final_color = vec4(texture(old_map, p.xy).r, 0.0f, 0.0f, 1.0f);
        //final_color = vec4(-p.z, 0.0f, 0.0f, 1.0f);
	}
    //*/

    //final_color.xyz = Ka*Ia*texval.xyz; //
    //final_color = p;

    //final_color = vec4( p.w/100, 0, 0, 1.0f );
    //final_color = vec4( 0, texture(shadow_map,p.xyz), 0, 1.0f );
    //final_color = vec4( 0, length(p)/100, 0, 1.0f );

}


