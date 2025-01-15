import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const PolicyEditor = () => {
  const [permissions, setPermissions] = useState({
    books: [],
    reviews: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  const roles = ['user', 'verified', 'moderator'];
  const permissionTypes = ['view', 'add', 'delete'];

  useEffect(() => {
    fetchCurrentPermissions();
  }, []);

  const fetchCurrentPermissions = async () => {
    try {
      const response = await fetch('/api/permissions');
      const data = await response.json();
      setPermissions({
        books: data.books_permissions || [],
        reviews: data.reviews_permissions || []
      });
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handlePermissionChange = (resource, role, permission, checked) => {
    setPermissions(prev => ({
      ...prev,
      [resource]: [
        { role, permission, granted: checked }
      ]
    }));
  };

  const savePermissions = async (resource) => {
    try {
      const response = await fetch(, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ permissions: permissions[resource] })
      });
      
      
      setSuccessMessage();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className=text-center p-4>Loading...</div>;
  if (error) return <Alert variant=destructive><AlertDescription>{error}</AlertDescription></Alert>;

  return (
    <div className=container mx-auto p-4>
      {successMessage && (
        <Alert className=mb-4>
          <AlertDescription>{successMessage}</AlertDescription>
        </Alert>
      )}
      
      {['books', 'reviews'].map(resource => (
        <Card key={resource} className=mb-8>
          <CardContent className=p-6>
            <h2 className=text-xl font-semibold mb-4 capitalize>
              {resource} Permissions
            </h2>
            
            <table className=w-full mb-4>
              <thead>
                <tr>
                  <th className=text-left>Role</th>
                  {permissionTypes.map(perm => (
                    <th key={perm} className=text-center capitalize>{perm}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {roles.map(role => (
                  <tr key={role}>
                    <td className=py-2 capitalize>{role}</td>
                    {permissionTypes.map(perm => (
                      <td key={perm} className=text-center>
                        <input
                          type=checkbox
                          className=h-5 w-5
                          checked={permissions[resource].some(
                            p => p.role === role && 
                                p.permission === perm && 
                                p.granted
                          )}
                          onChange={(e) => handlePermissionChange(
                            resource, 
                            role, 
                            perm, 
                            e.target.checked
                          )}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            
            <button
              onClick={() => savePermissions(resource)}
              className=w-full bg-purple-200 hover:bg-purple-300 text-gray-800 font-semibold py-2 px-4 rounded
            >
              Save {resource} Permissions
            </button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default PolicyEditor;
