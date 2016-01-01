#!/usr/bin/env python

import re
"""
int LoadModelFromFile(string modelPath, GLuint buffers[3], glm::mat3 *transform, glm::vec3 *translation)
{
  //Assume model is a .obj
  fprintf(stderr, "Attempting model load from %s...",modelPath.c_str());
  FILE* modelFile=fopen(modelPath.c_str(),"r");
  if(modelFile==NULL) {
      fprintf(stderr, " Failure\nCouldn't open model file '%s'\n", modelPath.c_str());
    return 0;
  }
  vector<glm::vec3> verts,normals;
  vector<glm::vec2> uvs;
  vector< unsigned int > vertexIndices, uvIndices, normalIndices;
  int line=0;
  int i;
  while (1){
    //Find first word of line
    char lineHeader[128];
    int res= fscanf(modelFile,"%s",lineHeader);
    if(res==EOF)
      break;
    if(strcmp(lineHeader,"vt")==0){
      //Process UV
      glm::vec2 uv;
      fscanf(modelFile,"%f %f\n",&uv.x,&uv.y);
      uv.y=1-uv.y;//(2+uv.y)/4;
      //uv.x=(2+uv.x)/4;
      uvs.push_back(uv);
    }else if(strcmp(lineHeader,"vn")==0){
      //Process normal
      glm::vec3 normal;
      fscanf(modelFile,"%f %f %f\n", &normal.x,&normal.y,&normal.z);
      normals.push_back(normal);
    }else if(strcmp(lineHeader,"v")==0){
      //Process vertex
      glm::vec3 vertex;
      fscanf(modelFile,"%f %f %f\n",&vertex.x,&vertex.y,&vertex.z);
      verts.push_back(vertex);
    }else if(strcmp(lineHeader,"f")==0){
      //Process face
      unsigned int vertexIndex[3],uvIndex[3],normalIndex[3];
      int matches=fscanf(modelFile,"%d/%d/%d %d/%d/%d %d/%d/%d\n",
			 &vertexIndex[0],&uvIndex[0],&normalIndex[0],
			 &vertexIndex[1],&uvIndex[1],&normalIndex[1],
			 &vertexIndex[2],&uvIndex[2],&normalIndex[2]);
      if (matches!=9){
	fprintf(stderr," Failure\nLine %d couldn't be read\n",line);
	return 0;
      }
      vertexIndices.push_back(vertexIndex[0]);
      vertexIndices.push_back(vertexIndex[1]);
      vertexIndices.push_back(vertexIndex[2]);
      
      uvIndices.push_back(uvIndex[0]);
      uvIndices.push_back(uvIndex[1]);
      uvIndices.push_back(uvIndex[2]);

      normalIndices.push_back(normalIndex[0]);
      normalIndices.push_back(normalIndex[1]);
      normalIndices.push_back(normalIndex[2]);
    }
    line++;
    //Done processing, loop back
  }
  //Transform verticies
  for(i=0; i<verts.size();i++){
      if (transform) {
          verts[i] = (*transform) * verts[i];
      }
      if (translation) {
          verts[i] = verts[i] + (*translation);
      }
  }
  for(i=0; i<normals.size();i++){
      if (transform) {
          normals[i] = (*transform) * normals[i];
      }
  }
  //Organize data into OpenGL compatible format
  unsigned int vertexIndicesLength=vertexIndices.size();
  float organizedVerticies[vertexIndicesLength*3];
  float organizedNormals[vertexIndicesLength*3];
  float organizedUVs[vertexIndicesLength*3];
  //Organize verticies
  for(i=0; i<vertexIndicesLength;i++){
      float *vertex = glm::value_ptr(verts[vertexIndices[i]-1]);
    //-1 because .obj starts from 1
      organizedVerticies[3*i+0]=vertex[0];
      organizedVerticies[3*i+1]=vertex[1];
      organizedVerticies[3*i+2]=vertex[2];
  }
  //Organize normals
  for(i=0; i<vertexIndicesLength;i++){
      float *normal = glm::value_ptr(normals[normalIndices[i]-1]);
    //-1 because .obj starts from 1
      organizedNormals[3*i+0]=normal[0];
      organizedNormals[3*i+1]=normal[1];
      organizedNormals[3*i+2]=normal[2];
  }
  //Organize uvs
  for(i=0; i<vertexIndicesLength;i++){
      float *uv = glm::value_ptr(uvs[uvIndices[i]-1]);
      organizedUVs[2*i+0]=uv[0];
      organizedUVs[2*i+1]=uv[1];
  }
  //Data is organized, create array of buffer and finish
  //Vertex=0
  //UV=1
  //Normal=2
  glGenBuffers(3,buffers);
  //Fill vertex buffer
  glBindBuffer(GL_ARRAY_BUFFER,buffers[0]);
  glBufferData(GL_ARRAY_BUFFER,
	       sizeof(glm::vec3)*vertexIndicesLength,
	       &organizedVerticies[0],
	       GL_STATIC_DRAW);
  //Fill uv buffer
  glBindBuffer(GL_ARRAY_BUFFER,buffers[1]);
  glBufferData(GL_ARRAY_BUFFER,
	       sizeof(glm::vec2)*vertexIndicesLength,
	       &organizedUVs[0],
	       GL_STATIC_DRAW);
  //Fill normal buffer
  glBindBuffer(GL_ARRAY_BUFFER,buffers[2]);
  glBufferData(GL_ARRAY_BUFFER,
	       sizeof(glm::vec3)*vertexIndicesLength,
	       &organizedNormals[0],
	       GL_STATIC_DRAW);
  fprintf(stderr, " Success\n");
  return vertexIndicesLength;
}

int LoadModelFromFile(string modelPath, GLuint buffers[3], float scale){
    glm::mat3 transform;
    transform = glm::mat3(scale);
    return LoadModelFromFile(modelPath, buffers, &transform, NULL);
}
"""
class c_obj(object):
    def __init__(self):
        self.vertices = []
        self.uv_map = []
        self.normals = []
        self.faces = []
        pass
    def load_from_file(self, f, transform=None, translation=None):
        def face_of_triple(vi,vti,vni):
            vi = int(vi)
            try:
                vti = int(vti)
            except:
                vti = None
            vni = int(vni)
            return (vi,vti,vni)
        float_re = r"(-*\d+(?:(?:\.\d*)|))"
        triple_re = r"(\d+)/((?:\d+)|)/(\d+)"
        uv_map_re      = re.compile("vt "+float_re+" "+float_re)
        normal_map_re  = re.compile("vn "+float_re+" "+float_re+" "+float_re)
        vertex_map_re  = re.compile("v "+float_re+" "+float_re+" "+float_re)
        face_re        = re.compile("f "+triple_re+"(.*)")
        face_triple_re = re.compile(" "+triple_re+"(.*)")
        self.uv_map = []
        self.normals = []
        self.vertices = []
        self.faces = []
        for l in f:
            m = uv_map_re.match(l)
            if m is not None:
                self.uv_map.append( (float(m.group(1)),float(m.group(2))) )
                pass
            m = normal_map_re.match(l)
            if m is not None:
                self.normals.append( (float(m.group(1)),float(m.group(2)),float(m.group(3))) )
                pass
            m = vertex_map_re.match(l)
            if m is not None:
                self.vertices.append( (float(m.group(1)),float(m.group(2)),float(m.group(3))) )
                pass
            m = face_re.match(l)
            if m is not None:
                face = []
                face.append(face_of_triple(m.group(1),m.group(2),m.group(3)))
                l = m.group(4)
                l.strip()
                while len(l)>0:
                    m = face_triple_re.match(l)
                    if m is None: break
                    face.append(face_of_triple(m.group(1),m.group(2),m.group(3)))
                    l = m.group(4)
                    l.strip()
                    pass
                self.faces.append(face)
                pass
            pass
        pass
